from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import DATABASE_URL

def now():
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def get_db():
    with SessionLocal() as db:
        yield db
