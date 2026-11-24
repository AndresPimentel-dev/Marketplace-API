from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import UsersTable


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, hashed_password: str) -> UsersTable:
        new = UsersTable(
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.now(UTC),
        )

        self.db.add(new)
        self.db.flush()
        self.db.refresh(new)

        return new

    # aqui si no user devolvera un none asi que declara en hint
    def get_user_by_email(self, email: str) -> UsersTable | None:
        stmt = select(UsersTable).where(UsersTable.email == email)

        return self.db.scalars(stmt).first()
