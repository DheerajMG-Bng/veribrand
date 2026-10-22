"""Populate precomputed cache using real AI results; reuse the just-recorded live run."""
import json
from datetime import datetime,timezone
from backend.app.db import Base,engine,SessionLocal
from backend.app.config import ROOT
from backend.app.models import KnowledgeItem
from backend.app.seed import seed,get_samples
from backend.app.review.engine import review_text,kb_hash
from sqlalchemy import select

def main():
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
        rows=[]
        for s in get_samples():
            result=review_text(db,s['text'],s['channel'],True)
            db.commit()
            rows.append(dict(sample_id=s['id'],text=s['text'],channel=s['channel'],result=result))
            print(f"Sample {s['id']}: {result['ai_status']}; model={result['model_used']}; cached={result['cached']}")
        data=dict(timestamp=datetime.now(timezone.utc).isoformat(),kb_hash=kb_hash(list(db.scalars(select(KnowledgeItem)))),reviews=rows)
        (ROOT/'backend/seed/precomputed_reviews.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
        print('Saved actual results. Unavailable results will not be loaded as precomputed AI reviews.')

if __name__=='__main__':
    main()
