from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import UUID, uuid7

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.db.base import BaseModel


class UserRole(StrEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(
            "dob IS NULL OR dob <= CURRENT_DATE",
            name="chk_users_dob",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        type_=Uuid(as_uuid=True), primary_key=True, default=uuid7
    )
    username: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    password: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    dob: Mapped[date] = mapped_column(type_=Date, nullable=False)
    email: Mapped[str] = mapped_column(type_=String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        type_=SqlEnum(
            UserRole,
            name="user_role",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=UserRole.STUDENT,
        server_default=UserRole.STUDENT.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
