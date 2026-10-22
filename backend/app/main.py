from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import select
from .db import Base, engine, SessionLocal, get_db
from .models import KnowledgeItem
from .seed import seed, get_samples

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield

app = FastAPI(title='VeriBrand', lifespan=lifespan)

@app.get('/api/health')
def health():
    return {'status': 'ok', 'demo_roles': True}

@app.get('/api/knowledge')
def knowledge(db=Depends(get_db)):
    return list(db.scalars(select(KnowledgeItem).order_by(KnowledgeItem.code)))

@app.get('/api/samples')
def samples():
    return get_samples()
