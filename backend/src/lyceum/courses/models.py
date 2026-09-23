from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class CourseCategory(BaseModel):
    __tablename__ = "course_categories"

    course_id: Mapped[UUID] = mapped_column(
        ForeignKey("courses.id"),
        primary_key=True,
    )
    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("categories.id"),
        primary_key=True,
    )


class Course(BaseModel):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("slug", "uq_courses_slug"),
        CheckConstraint(sqltext="rating_count >= 0", name="chk_courses_rating_count"),
        CheckConstraint(
            sqltext="enrollment_count >= 0", name="chk_courses_enrollment_count"
        ),
        CheckConstraint(
            sqltext="total_duration_mins >= 1", name="chk_courses_total_duration_mins"
        ),
    )

    instructor_id: Mapped[UUID] = mapped_column(
        ForeignKey(Instructor.user_id), nullable=False
    )
    instructor_name: Mapped[str] = mapped_column(type_=String(200), nullable=False)
    title: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    slug: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    short_description: Mapped[str] = mapped_column(type_=String(255), nullable=True)
    description: Mapped[str] = mapped_column(type_=Text(), nullable=True)
    thumbnail: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    level: Mapped[CourseLevel] = mapped_column(
        type_=SqlEnum(
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
        type_=SqlEnum(
            CourseStatus,
            name="status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=CourseStatus.DRAFT,
        server_default=CourseStatus.DRAFT.value,
    )
    avg_rating: Mapped[float] = mapped_column(type_=Float(), nullable=True)
    rating_count: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    enrollment_count: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    total_duration_mins: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    published_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )

    categories: Mapped[list[CourseCategory]] = relationship(
        secondary=CourseCategory, back_populates="courses"
    )
