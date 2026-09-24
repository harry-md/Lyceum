from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from lyceum.categories.models import Category
from lyceum.db.models import BaseModel
from lyceum.users.models import Instructor


class CourseLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ALL_LEVEL = "all_level"


class CourseStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


course_categories = Table(
    "course_categories",
    BaseModel.metadata,
    Column(ForeignKey("courses.id"), name="course_id", primary_key=True),
    Column(
        ForeignKey("categories.id"), name="category_id", primary_key=True, index=True
    ),
)


class Course(BaseModel):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_courses_slug"),
        CheckConstraint(
            "avg_rating >= 0 AND avg_rating <= 5", name="chk_courses_avg_rating"
        ),
        CheckConstraint("rating_count >= 0", name="chk_courses_rating_count"),
        CheckConstraint("price >= 0", name="chk_courses_price"),
        CheckConstraint(
            sqltext="enrollment_count >= 0", name="chk_courses_enrollment_count"
        ),
        CheckConstraint(
            sqltext="total_duration_mins >= 0", name="chk_courses_total_duration_mins"
        ),
    )

    instructor_id: Mapped[UUID] = mapped_column(
        ForeignKey(Instructor.user_id), nullable=False, index=True
    )
    instructor_name: Mapped[str] = mapped_column(type_=String(200), nullable=False)
    title: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    slug: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    short_description: Mapped[str | None] = mapped_column(
        type_=String(255), nullable=True
    )
    description: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    thumbnail: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    level: Mapped[CourseLevel] = mapped_column(
        type_=Enum(
            CourseLevel,
            name="level",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=CourseLevel.ALL_LEVEL,
        server_default=CourseLevel.ALL_LEVEL.value,
    )
    status: Mapped[CourseStatus] = mapped_column(
        type_=Enum(
            CourseStatus,
            name="course_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=CourseStatus.DRAFT,
        server_default=CourseStatus.DRAFT.value,
    )
    price: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=10, scale=2), nullable=False
    )
    avg_rating: Mapped[float | None] = mapped_column(type_=Float(), nullable=True)
    rating_count: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    enrollment_count: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    total_duration_mins: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    published_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )

    categories: Mapped[list[Category]] = relationship(secondary=course_categories)
