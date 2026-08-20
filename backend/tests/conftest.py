import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base


@pytest.fixture
def db_session():
    engine = create_engine(
        settings.test_database_url,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(engine)

    TestSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    with TestSessionLocal() as session:
        yield session

    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()