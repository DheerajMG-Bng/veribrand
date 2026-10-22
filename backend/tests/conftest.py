import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.db import Base
from backend.app.seed import seed

@pytest.fixture
def db():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        seed(session)
        yield session
    engine.dispose()

@pytest.fixture
def kb(db):
    from sqlalchemy import select
    from backend.app.models import KnowledgeItem
    return list(db.scalars(select(KnowledgeItem)))
