import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import UserRole, UsersTable

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def create_admin():
    db = SessionLocal()
    try:
        existing = db.query(UsersTable).filter(UsersTable.email == ADMIN_EMAIL).first()
        if existing:
            print("admin already created")
            return existing
        hashed = hash_password(password=ADMIN_PASSWORD)
        new = UsersTable(
            email=ADMIN_EMAIL,
            hashed_password=hashed,
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        print("admin successfully created")
        return new
    except SQLAlchemyError as e:
        db.rollback()
        print(f"error creating admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
