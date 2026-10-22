"""Exercise the public demo with fictional data and save exact observed evidence.

No secrets are read or printed. Does not reset shared demo data. AI text is unique
per run to distinguish a real provider call from cached precomputed samples.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpx

BASE='https://veribrand.onrender.com'
OUT=Path('docs/submission/evidence')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    events=[]
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    with httpx.Client(base_url=BASE,timeout=150,follow_redirects=True) as c:
        def req(method,path,body=None,role='creator',expected=200):
            r=c.request(method,'/api'+path,json=body,headers={'X-Role':role})
            assert r.status_code==expected,f'{method} {path}: expected {expected}, got {r.status_code}: {r.text[:200]}'
            return r.json()
        def record(feature,details):
            events.append({'feature':feature,'result':'PASS','details':details})
            print(feature+': PASS',flush=True)
        knowledge=req('GET','/knowledge')
        samples=req('GET','/samples')
        record('knowledge and samples',{'knowledge_count':len(knowledge),'sample_count':len(samples)})
        before=req('GET','/ai/status')
        text=f'Campaign reference {stamp}. Acme Hydrate is recommended by every professional athlete in India.'
        d=req('POST','/contents',dict(title='Submission verification - genuine AI '+stamp,channel='social',text=text))
        ai=req('POST',f"/contents/{d['id']}/review",{'use_ai':True})
        after=req('GET','/ai/status')
        delta=sum(x['tokens_today'] for x in after['models'])-sum(x['tokens_today'] for x in before['models'])
        ai_evidence={'content_id':d['id'],'before':before,'after':after,'token_delta':delta,
                     'ai_status':ai['ai_status'],'model_used':ai['model_used'],'cached':ai['cached'],'findings':ai['content']['findings']}
        (OUT/'live-ai.json').write_text(json.dumps(ai_evidence,indent=2),encoding='utf-8')
        assert ai['ai_status']=='ok' and not ai['cached'] and delta>0,'Live provider call / usage accounting failed.'
        assert any(f['origin']=='ai' and f['verification']=='unverified' for f in ai['content']['findings']),'Expected an AI-origin unverified endorsement finding.'
        record('uncached AI and token accounting',{'content_id':d['id'],'model':ai['model_used'],'token_delta':delta,'ai_findings':len(ai['content']['findings'])})
        d=req('POST','/contents',dict(title='Submission verification - full workflow '+stamp,channel='social',text='AcmeHydrate is guaranteed to cure fatigue.'))
        cid=d['id']
        def post(action,body=None,role='creator',expected=200):
            return req('POST',f'/contents/{cid}/{action}',body or {},role,expected)
        reviewed=post('review',{'use_ai':False})
        fs=reviewed['content']['findings']
        assert fs and all(f['verification']=='verified' and f['source_code'] in {k['code'] for k in knowledge} for f in fs)
        record('rules-only review and real citations',{'content_id':cid,'codes':sorted({f['source_code'] for f in fs})})
        f=next(f for f in fs if f['source_code']=='C-11')
        response=req('POST',f"/findings/{f['id']}/decision",{'decision':'rejected'},expected=422)
        record('reject requires reason',response)
        for f in fs:
            decision={'decision':'accepted'} if f['source_code']=='T-02' else {'decision':'edited','edited_text':''} if f['source_code']=='C-07' else {'decision':'rejected','reason':'Fictional submission test: retain risk solely to verify Reviewer escalation.'}
            req('POST',f"/findings/{f['id']}/decision",decision)
        record('accept edit and reject',{'decisions':['accepted','edited','rejected']})
        applied=post('apply')
        assert applied['versions'][0]['version_no']==2 and applied['versions'][0]['text']=='Acme Hydrate is  to cure fatigue.'
        record('apply creates new version',{'version':2,'text':applied['versions'][0]['text']})
        post('submit',expected=409)
        r=post('review',{'use_ai':False})
        for f in r['content']['findings']:
            req('POST',f"/findings/{f['id']}/decision",{'decision':'rejected','reason':'Fictional test of retained medical-risk routing.'})
        assert post('submit')['status']=='in_review'
        post('approve',expected=403)
        assert post('approve',role='manager')['status']=='pending_reviewer'
        assert post('reviewer-signoff',{'reason':'Fictional submission verification; no publication authorised.'},'reviewer')['status']=='approved'
        record('submit manager routing and Reviewer sign-off',{'content_id':cid,'final_status':'approved','wrong_role_status':403})
        assert post('return',{'comment':'Submission verification: revise the wording.'},'manager')['status']=='changes_requested'
        post('versions',{'text':'Acme Hydrate comes in 500 ml, 1 L and 5 L packs.'})
        assert post('review',{'use_ai':False})['findings']==[]
        post('submit')
        assert post('approve',role='manager')['status']=='approved'
        record('return comment manual version resubmit',{'content_id':cid,'version':3,'status':'approved'})
        post('comments',{'text':'Submission verification comment.'})
        detail=req('GET',f'/contents/{cid}')
        diff=req('GET',f'/contents/{cid}/diff?from=1&to=3')
        audit=req('GET',f'/contents/{cid}/audit')
        assert len(detail['versions'])==3 and diff['before']!=diff['after']
        assert len(detail['comments'])==2 and any(a['action']=='reviewer_signed_off' for a in audit)
        record('versions diff comments audit',{'content_id':cid,'versions':3,'comments':len(detail['comments']),'audit_entries':len(audit),'before':diff['before'],'after':diff['after']})
        req('POST','/contents',dict(title='Submission length boundary '+stamp,channel='social',text='a'*5000))
        error=req('POST','/contents',dict(title='Submission overlength '+stamp,channel='social',text='a'*5001),expected=422)
        record('5000 character limit',{'5000':'accepted','5001':error})
        # Create a temporary item rather than changing an approved brand policy.
        item=req('POST','/knowledge',dict(kind='guideline',code='G-98',title='Submission verification temporary item',text='Temporary verification note, not brand policy.',meta={}),role='admin')
        payload={k:item[k] for k in ['kind','code','title','text','meta','valid_until']}
        payload['title']='Submission verification edited item'
        updated=req('PUT',f"/knowledge/{item['id']}",payload,role='admin')
        assert updated['title']==payload['title']
        req('DELETE',f"/knowledge/{item['id']}",role='admin')
        record('admin knowledge add edit delete',{'temporary_code':'G-98','restored_count':len(req('GET','/knowledge'))})
        # Finish with the limiter, so it cannot block the workflow/AI checks.
        clean=req('POST','/contents',dict(title='Submission verification - limiter '+stamp,channel='social',text='Acme Hydrate is available in 1 L packs.'))
        limited=None
        for attempt in range(11):
            r=c.post(f"/api/contents/{clean['id']}/review",json={'use_ai':False},headers={'X-Role':'creator'})
            if r.status_code==429:
                limited={'status':429,'detail':r.json()['detail'],'retry_after':r.headers.get('Retry-After')}
                break
            assert r.status_code==200,r.text[:200]
        assert limited,'Limiter was not observed.'
        record('friendly rate limit',limited)
        result={'timestamp':datetime.now(timezone.utc).isoformat(),'base_url':BASE,'events':events,'workflow_content_id':cid,'ai_content_id':ai_evidence['content_id']}
        (OUT/'live-feature-verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print('Saved evidence. No shared demo reset was performed.',flush=True)

if __name__=='__main__':
    main()
