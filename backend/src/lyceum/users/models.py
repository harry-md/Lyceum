from datetime import UTC, date, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lyceum.db.models import Base, BaseModel


class UserRole(StrEnum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(BaseModel):
    __tablename__ = "users"
    __table_args__: tuple[UniqueConstraint, UniqueConstraint, CheckConstraint] = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),
        CheckConstraint(sqltext="dob <= CURRENT_DATE", name="chk_users_dob"),
    )

    username: Mapped[str] = mapped_column(type_=String(length=100), nullable=False)
    password: Mapped[str] = mapped_column(type_=String(length=100), nullable=False)
    first_name: Mapped[str] = mapped_column(type_=String(length=100), nullable=False)
    last_name: Mapped[str] = mapped_column(type_=String(length=100), nullable=False)
    dob: Mapped[date] = mapped_column(type_=Date, nullable=False)
    email: Mapped[str] = mapped_column(type_=String(length=100), nullable=False)
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

    instructor: Mapped["Instructor"] = relationship(back_populates="user")


class Instructor(Base):
    __tablename__ = "instructors"
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), primary_key=True)
    headline: Mapped[str] = mapped_column(type_=String(100), nullable=True)
    bio: Mapped[str] = mapped_column(type_=Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
