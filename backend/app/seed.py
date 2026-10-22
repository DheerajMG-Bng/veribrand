import json
from datetime import date
from sqlalchemy import select
from .config import ROOT
from .models import KnowledgeItem, Content
from .services.content import create_content

def seed(db, demo=False):
    if not db.scalar(select(KnowledgeItem.id).limit(1)):
        for row in json.loads((ROOT / 'backend/seed/knowledge.json').read_text(encoding='utf-8')):
            if row.get('valid_until'):
                row['valid_until'] = date.fromisoformat(row['valid_until'])
            db.add(KnowledgeItem(**row))
        db.flush()
    if demo and not db.scalar(select(Content.id).limit(1)):
        samples = get_samples()
        create_content(db, 'Campaign launch — needs review', samples[0]['channel'], samples[0]['text'], source='sample')
        clean = create_content(db, 'Classic range — ready for manager', samples[1]['channel'], samples[1]['text'], source='sample')
        from .review.engine import run_review
        from .services.content import latest, audit
        from .services.workflow import submit_content, approve_content
        run_review(db, latest(db, clean.id), clean.channel, False)
        audit(db, 'creator', 'review_completed', clean.id, {'seed': True})
        submit_content(db, clean, 'creator')
        approved = create_content(db, 'Pack announcement — approved example', 'social', 'Acme Hydrate is available in 500 ml, 1 L and 5 L packs.', source='sample')
        run_review(db, latest(db, approved.id), approved.channel, False)
        audit(db, 'creator', 'review_completed', approved.id, {'seed': True})
        submit_content(db, approved, 'creator')
        approve_content(db, approved, 'manager')
    db.commit()

def get_samples():
    return json.loads((ROOT / 'backend/seed/samples.json').read_text(encoding='utf-8'))
