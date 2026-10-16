import os
from datetime import UTC, datetime

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import UsersTable

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


def create_admin():
    db = SessionLocal()
    try:
        existing = db.query(UsersTable).filter(UsersTable.email == ADMIN_EMAIL).first()
        if existing:
            return print("admin already created")
        hashed = hash_password(password=ADMIN_PASSWORD)
        new = UsersTable(
            email=ADMIN_EMAIL,
            hashed_password=hashed,
            role="admin",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        db.add(new)
        db.commit()
        print(new)
        return new
    except SQLAlchemyError as e:
        db.rollback()
        print(f"error creating admin: {e}")


if __name__ == "__main__":
    create_admin()
