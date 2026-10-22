from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import select
from .db import Base, engine, SessionLocal, get_db
from .models import KnowledgeItem
from .seed import seed, get_samples
from .routes.api import router
from .review.engine import load_precomputed
from .config import ROOT

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db,demo=True)
        load_precomputed(db)
    yield

app = FastAPI(title='VeriBrand', lifespan=lifespan)
app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_error(request:Request, exc:RequestValidationError):
    errors=[]
    for error in exc.errors():
        field=str(error['loc'][-1])
        message='Drafts must be 5,000 characters or fewer.' if field=='text' and error['type']=='string_too_long' else f"{field}: {error['msg']}"
        errors.append(message)
    return JSONResponse(status_code=422,content={'detail':' '.join(errors)})

@app.exception_handler(Exception)
async def unexpected_error(request:Request,exc:Exception):
    return JSONResponse(status_code=500,content={'detail':'Something went wrong. Please retry; if it persists, reload the draft.'})

@app.get('/api/health')
def health():
    return {'status': 'ok', 'demo_roles': True}

@app.get('/api/knowledge')
def knowledge(db=Depends(get_db)):
    return list(db.scalars(select(KnowledgeItem).order_by(KnowledgeItem.code)))

@app.get('/api/samples')
def samples():
    return get_samples()

static=ROOT/'backend/app/static'
if (static/'assets').exists():
    app.mount('/assets',StaticFiles(directory=static/'assets'),name='assets')

@app.get('/{path:path}',include_in_schema=False)
def spa(path:str):
    if path=='api' or path.startswith('api/'):
        return JSONResponse(status_code=404,content={'detail':'API endpoint not found.'})
    target=(static/path).resolve()
    if target.is_relative_to(static.resolve()) and target.is_file():
        return FileResponse(target)
    if (static/'index.html').exists():
        return FileResponse(static/'index.html')
    return JSONResponse(status_code=503,content={'detail':'Frontend build is not available yet.'})
