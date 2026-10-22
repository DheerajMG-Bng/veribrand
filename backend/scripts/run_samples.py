"""Run all samples; --ai makes exactly one review request per sample (fallback may retry)."""
import argparse
import json
from backend.app.db import Base, engine, SessionLocal
from backend.app.seed import seed, get_samples
from backend.app.review.engine import review_text

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ai',action='store_true')
    parser.add_argument('--cached-only',action='store_true',help='Require existing AI cache entries; makes no network requests.')
    args=parser.parse_args()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
        hits=total=0
        rows=[]
        for sample in get_samples():
            if args.cached_only:
                from backend.app.models import KnowledgeItem, ReviewCache
                from backend.app.review.engine import cache_key
                from sqlalchemy import select
                knowledge=list(db.scalars(select(KnowledgeItem)))
                if not db.get(ReviewCache,cache_key(sample['text'],sample['channel'],knowledge,args.ai)):
                    raise RuntimeError('Missing cache entry. No network call made.')
            result=review_text(db,sample['text'],sample['channel'],args.ai)
            db.commit()
            codes={c for f in result['findings'] for c in [f['source_code'],*f['also_cites']] if c}
            expected=set(sample['expected_codes'])
            hits+=len(codes & expected)
            total+=len(expected)
            row=dict(sample=sample['id'],expected=sorted(expected),found=sorted(codes),findings=len(result['findings']),
                     unverified=sum(f['verification']=='unverified' for f in result['findings']),ai_status=result['ai_status'],model=result['model_used'],cached=result['cached'])
            rows.append(row)
            print(json.dumps(row))
        print(json.dumps(dict(mode='AI' if args.ai else 'rules_only',code_recall=f'{hits}/{total}',recall=hits/total,
                              sample_2_false_positives=rows[1]['findings'])))

if __name__=='__main__':
    main()
