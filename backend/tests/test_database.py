from sqlalchemy import text

from app.db.session import engine, SessionLocal
from app.models.engineering_change import (
    ChangeStatus,
    EngineeringChange,
)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
              

def test_create_engineering_change(db_session):
    change = EngineeringChange(
        change_number="ECR-TEST-001",
        title="Test engineering change",
        description="Automated integration test.",
    )

    db_session.add(change)
    db_session.commit()
    db_session.refresh(change)

    assert change.id is not None
    assert change.status == ChangeStatus.DRAFT