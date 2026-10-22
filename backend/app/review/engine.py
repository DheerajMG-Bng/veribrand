import hashlib
import json
import re
from sqlalchemy import select, delete
from ..db import now
from ..models import KnowledgeItem, Finding, ReviewCache
from .rules import run_rules
from .validator import validate
from .llm import analyse

def kb_hash(knowledge):
    data = [dict(code=k.code, kind=k.kind, title=k.title, text=k.text, meta=k.meta, valid_until=str(k.valid_until)) for k in sorted(knowledge, key=lambda k:k.code)]
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def cache_key(text, channel, knowledge, use_ai):
    normalized = re.sub(r'\s+', ' ', text).strip()
    return hashlib.sha256(json.dumps([normalized, channel, kb_hash(knowledge), use_ai], ensure_ascii=False).encode()).hexdigest()

def review_text(db, text, channel, use_ai):
    knowledge = list(db.scalars(select(KnowledgeItem)))
    key = cache_key(text, channel, knowledge, use_ai)
    cached = db.get(ReviewCache, key)
    if cached:
        result = dict(cached.result)
        # Re-ground against exact current whitespace; stored offsets may belong
        # to a whitespace-equivalent draft.
        rules = run_rules(text, channel, knowledge)
        result['findings'] = validate(text, channel, knowledge, rules, result.get('ai_result'))
        result['cached'] = True
        return result
    rules = run_rules(text, channel, knowledge)
    ai, model, note = analyse(db, text, channel, knowledge, rules) if use_ai else (None, None, 'AI is off. Showing rule-based results.')
    result = dict(findings=validate(text, channel, knowledge, rules, ai), ai_status=('ok' if model else 'unavailable') if use_ai else 'rules_only',
                  model_used=model, cached=False, note=note, ai_result=ai)
    # Do not freeze transient provider failures in the cache.
    if not use_ai or model:
        db.add(ReviewCache(key=key, result=result))
        db.flush()
    return result

def run_review(db, version, channel, use_ai):
    result = review_text(db, version.text, channel, use_ai)
    db.execute(delete(Finding).where(Finding.version_id == version.id))
    for finding in result['findings']:
        db.add(Finding(version_id=version.id, **{k:v for k,v in finding.items() if k != 'id'}))
    version.reviewed_at = now()
    db.flush()
    return {k:v for k,v in result.items() if k != 'ai_result'}

def load_precomputed(db):
    from ..config import ROOT
    path = ROOT / 'backend/seed/precomputed_reviews.json'
    if not path.exists():
        return 0
    knowledge = list(db.scalars(select(KnowledgeItem)))
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('kb_hash') != kb_hash(knowledge):
        return 0
    count = 0
    for row in data.get('reviews', []):
        result = row['result']
        if result.get('ai_status') != 'ok':
            continue
        key = cache_key(row['text'], row['channel'], knowledge, True)
        result['precomputed_at'] = data['timestamp']
        if not db.get(ReviewCache, key):
            db.add(ReviewCache(key=key, result=result))
            count += 1
    db.commit()
    return count
