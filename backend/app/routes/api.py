from collections import defaultdict, deque
from threading import Lock
import difflib
import time
import re
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, delete
from sqlalchemy.inspection import inspect
from ..db import get_db, now
from .. import models as m, schemas as s, config
from ..roles import get_role, require
from ..seed import seed
from ..services.content import audit, create_content, get_content, latest, findings_for, editable, add_version, apply_text
from ..services.workflow import submit_content, approve_content
from ..review.engine import run_review, load_precomputed
from ..review.budget import state, used_today, minute_used

router=APIRouter(prefix='/api')
limits=defaultdict(deque)
limit_lock=Lock()

def as_dict(obj):
    return {column.key:getattr(obj,column.key) for column in inspect(obj).mapper.column_attrs}

def detail(db,item):
    versions=list(db.scalars(select(m.ContentVersion).where(m.ContentVersion.content_id==item.id).order_by(m.ContentVersion.version_no.desc())))
    return {**as_dict(item),'versions':[as_dict(v) for v in versions],
            'findings':[as_dict(f) for f in findings_for(db,versions[0].id)],
            'comments':[as_dict(c) for c in db.scalars(select(m.Comment).where(m.Comment.content_id==item.id).order_by(m.Comment.id))]}

@router.get('/ai/status')
def ai_status(db=Depends(get_db)):
    models=[{'model':model,'tokens_today':used_today(db,model),'tokens_this_minute':minute_used(model),'state':state(db,model)} for model in config.MODELS]
    return {'enabled':bool(config.GROQ_API_KEY),'models':models,'state':('ok' if any(x['state']=='ok' for x in models) else 'exhausted' if all(x['state']=='exhausted' for x in models) else 'busy') if config.GROQ_API_KEY else 'rules_only'}

def validate_meta(data):
    meta=data.meta
    check=meta.get('check')
    allowed={'patterns','regex','hype_punctuation','max_hashtags','disclosure','expired_offer','price_mismatch','year_conflict'}
    if check is None:
        return
    if check not in allowed or meta.get('severity','medium') not in {'low','medium','high'}:
        raise HTTPException(422,'Choose a supported rule check and severity.')
    if check in {'patterns','regex','expired_offer'}:
        if not isinstance(meta.get('patterns'),list) or not meta['patterns'] or any(not isinstance(p,str) or not p or len(p)>200 for p in meta['patterns']):
            raise HTTPException(422,'Rule patterns must be a nonempty list of short strings.')
        if check=='regex':
            for pattern in meta['patterns']:
                try:
                    re.compile(pattern)
                except re.error:
                    raise HTTPException(422,'Invalid regular expression.')
                if re.search(r'\([^)]*[+*][^)]*\)[+*{]',pattern):
                    raise HTTPException(422,'Nested regex repetition is not supported.')
    for key in ('also_cites','channels','markers','trigger','symbols','product_patterns'):
        if key in meta and (not isinstance(meta[key],list) or any(not isinstance(v,str) or not v for v in meta[key])):
            raise HTTPException(422,f'{key} must be a list of nonempty strings.')
    required={'price_mismatch':('approved_price','symbols','product_patterns'),'year_conflict':('approved_year','trigger'),'disclosure':('channels','markers')}
    if any(key not in meta for key in required.get(check,())):
        raise HTTPException(422,'This rule is missing required metadata.')
    for key in ('max','max_exclamations','approved_price','approved_year'):
        if key in meta and (not isinstance(meta[key],(int,float)) or meta[key]<0):
            raise HTTPException(422,f'{key} must be a nonnegative number.')
    for key in ('max','max_exclamations','approved_year'):
        if key in meta and (not isinstance(meta[key],int) or isinstance(meta[key],bool)):
            raise HTTPException(422,f'{key} must be an integer.')
    for key in ('replacement','replacement_prefix'):
        if key in meta and not isinstance(meta[key],str):
            raise HTTPException(422,f'{key} must be text.')

@router.post('/knowledge')
def add_knowledge(data:s.KnowledgeInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'admin')
    validate_meta(data)
    if db.scalar(select(m.KnowledgeItem).where(m.KnowledgeItem.code==data.code)):
        raise HTTPException(409,'This knowledge code already exists.')
    item=m.KnowledgeItem(**data.model_dump())
    db.add(item)
    audit(db,role,'knowledge_added',detail={'code':data.code})
    db.commit()
    return item

@router.put('/knowledge/{item_id}')
def update_knowledge(item_id:int,data:s.KnowledgeInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'admin')
    validate_meta(data)
    item=db.get(m.KnowledgeItem,item_id)
    if not item:
        raise HTTPException(404,'Knowledge item not found.')
    duplicate=db.scalar(select(m.KnowledgeItem).where(m.KnowledgeItem.code==data.code,m.KnowledgeItem.id!=item_id))
    if duplicate:
        raise HTTPException(409,'This knowledge code already exists.')
    for key,value in data.model_dump().items():
        setattr(item,key,value)
    audit(db,role,'knowledge_updated',detail={'code':item.code})
    db.commit()
    return item

@router.delete('/knowledge/{item_id}')
def delete_knowledge(item_id:int,db=Depends(get_db),role=Depends(get_role)):
    require(role,'admin')
    item=db.get(m.KnowledgeItem,item_id)
    if not item:
        raise HTTPException(404,'Knowledge item not found.')
    audit(db,role,'knowledge_deleted',detail={'code':item.code})
    db.delete(item)
    db.commit()
    return {'ok':True}

@router.post('/demo/reset')
def reset(db=Depends(get_db),role=Depends(get_role)):
    require(role,'admin')
    # Preserve usage across resets: a demo reset must not reset provider budgets.
    for model in (m.Finding,m.Comment,m.AuditLog,m.ContentVersion,m.Content,m.ReviewCache,m.KnowledgeItem):
        db.execute(delete(model))
    seed(db,demo=True)
    load_precomputed(db)
    audit(db,role,'demo_reset',detail={'usage_preserved':True})
    db.commit()
    return {'ok':True}

@router.get('/contents')
def contents(db=Depends(get_db)):
    return list(db.scalars(select(m.Content).order_by(m.Content.updated_at.desc())))

@router.post('/contents')
def new_content(data:s.Draft,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    item=create_content(db,data.title,data.channel,data.text,role)
    db.commit()
    return detail(db,item)

@router.get('/contents/{content_id}')
def content(content_id:int,db=Depends(get_db)):
    return detail(db,get_content(db,content_id))

@router.post('/contents/{content_id}/review')
def review(content_id:int,data:s.ReviewInput,request:Request,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    item=get_content(db,content_id)
    editable(item)
    ip=request.client.host if request.client else 'unknown'
    with limit_lock:
        clock=time.monotonic()
        # Drop idle clients to keep the demonstration limiter bounded.
        for key in list(limits):
            while limits[key] and limits[key][0]<clock-60:
                limits[key].popleft()
            if not limits[key]:
                del limits[key]
        queue=limits[ip]
        if len(queue)>=10:
            raise HTTPException(429,'You have run 10 reviews this minute. Please wait a minute and try again.',headers={'Retry-After':'60'})
        queue.append(clock)
    version=latest(db,content_id)
    existing=findings_for(db,version.id)
    if any(f.decision!='pending' for f in existing):
        raise HTTPException(409,'Apply your decisions or create a new version before re-running review. This preserves your decision history.')
    result=run_review(db,version,item.channel,data.use_ai)
    audit(db,role,'review_completed',content_id,{'version':version.version_no,'ai_status':result['ai_status'],'model':result['model_used'],'cached':result['cached']},ai=data.use_ai)
    db.commit()
    return {**result,'content':detail(db,item)}

@router.post('/findings/{finding_id}/decision')
def decision(finding_id:int,data:s.DecisionInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    finding=db.get(m.Finding,finding_id)
    if not finding:
        raise HTTPException(404,'Finding not found.')
    version=db.get(m.ContentVersion,finding.version_id)
    item=get_content(db,version.content_id)
    editable(item)
    if latest(db,item.id).id!=version.id:
        raise HTTPException(409,'Decisions can only be made on the latest version.')
    if data.decision=='accepted' and (finding.replacement is None or finding.verification=='unverified'):
        raise HTTPException(422,'This finding has no verified replacement. Edit the phrase or reject with a reason.')
    if data.decision=='edited' and data.edited_text is None:
        raise HTTPException(422,'Enter replacement text. An empty string removes the phrase.')
    if data.decision=='rejected' and not (data.reason or '').strip():
        raise HTTPException(422,'Explain why you are overriding this finding.')
    finding.decision=data.decision
    finding.edited_text=data.edited_text if data.decision=='edited' else None
    finding.decision_reason=data.reason
    finding.decided_by_role,finding.decided_at=role,now()
    audit(db,role,'finding_decided',item.id,{'finding_id':finding.id,'decision':data.decision,'edited_text':finding.edited_text,'reason':data.reason},ai=finding.origin=='ai')
    db.commit()
    return as_dict(finding)

@router.post('/contents/{content_id}/apply')
def apply(content_id:int,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    item=get_content(db,content_id)
    editable(item)
    version=latest(db,content_id)
    findings=findings_for(db,version.id)
    if not any(f.decision in {'accepted','edited'} for f in findings):
        raise HTTPException(409,'Accept or edit at least one finding before applying decisions.')
    text=apply_text(version.text,findings)
    add_version(db,item,text,role,'applied_fixes')
    audit(db,role,'decisions_applied',content_id,{'from_version':version.version_no},ai=any(f.origin=='ai' and f.decision in {'accepted','edited'} for f in findings))
    db.commit()
    return detail(db,item)

@router.post('/contents/{content_id}/versions')
def version(content_id:int,data:s.VersionInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    item=get_content(db,content_id)
    add_version(db,item,data.text,role)
    db.commit()
    return detail(db,item)

@router.get('/contents/{content_id}/diff')
def diff(content_id:int,request:Request,db=Depends(get_db)):
    get_content(db,content_id)
    versions={v.version_no:v for v in db.scalars(select(m.ContentVersion).where(m.ContentVersion.content_id==content_id))}
    try:
        before=versions[int(request.query_params.get('from','1'))]
        after=versions[int(request.query_params.get('to',str(max(versions))))]
    except (KeyError,ValueError):
        raise HTTPException(404,'Choose valid version numbers.')
    return {'from':before.version_no,'to':after.version_no,'before':before.text,'after':after.text,
            'diff':'\n'.join(difflib.unified_diff(before.text.splitlines(),after.text.splitlines(),fromfile=f'v{before.version_no}',tofile=f'v{after.version_no}',lineterm=''))}

@router.post('/contents/{content_id}/submit')
def submit(content_id:int,db=Depends(get_db),role=Depends(get_role)):
    require(role,'creator')
    item=get_content(db,content_id)
    submit_content(db,item,role)
    db.commit()
    return detail(db,item)

@router.post('/contents/{content_id}/approve')
def approve(content_id:int,db=Depends(get_db),role=Depends(get_role)):
    require(role,'manager')
    item=get_content(db,content_id)
    approve_content(db,item,role)
    db.commit()
    return detail(db,item)

@router.post('/contents/{content_id}/reviewer-signoff')
def signoff(content_id:int,data:s.ReasonInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'reviewer')
    item=get_content(db,content_id)
    if item.status!='pending_reviewer':
        raise HTTPException(409,'This content is not awaiting Reviewer sign-off.')
    if not data.reason.strip():
        raise HTTPException(422,'A sign-off reason is required.')
    item.status,item.updated_at='approved',now()
    audit(db,role,'reviewer_signed_off',content_id,{'reason':data.reason})
    db.commit()
    return detail(db,item)

@router.post('/contents/{content_id}/return')
def return_content(content_id:int,data:s.ReturnInput,db=Depends(get_db),role=Depends(get_role)):
    require(role,'manager','reviewer')
    item=get_content(db,content_id)
    allowed={'manager':{'in_review','approved'},'reviewer':{'pending_reviewer','approved'}}
    if item.status not in allowed[role]:
        raise HTTPException(409,'This content is not at a stage that your role can return.')
    if not data.comment.strip():
        raise HTTPException(422,'Explain what the creator needs to change.')
    item.status,item.updated_at='changes_requested',now()
    db.add(m.Comment(content_id=content_id,role=role,text=data.comment))
    audit(db,role,'returned',content_id,{'comment':data.comment})
    db.commit()
    return detail(db,item)

@router.post('/contents/{content_id}/comments')
def comment(content_id:int,data:s.CommentInput,db=Depends(get_db),role=Depends(get_role)):
    get_content(db,content_id)
    if not data.text.strip():
        raise HTTPException(422,'Enter a comment before posting.')
    db.add(m.Comment(content_id=content_id,role=role,text=data.text))
    audit(db,role,'comment_added',content_id,{'text':data.text})
    db.commit()
    return {'ok':True}

@router.get('/contents/{content_id}/audit')
def audit_trail(content_id:int,db=Depends(get_db)):
    get_content(db,content_id)
    return list(db.scalars(select(m.AuditLog).where(m.AuditLog.content_id==content_id).order_by(m.AuditLog.id)))
