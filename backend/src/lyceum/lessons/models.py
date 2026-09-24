from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.chapters.models import Chapter
from lyceum.db.models import BaseModel


class LessonStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class Lesson(BaseModel):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("chapter_id", "order", name="uq_lessons_chapter_order"),
        CheckConstraint('"order" >= 1', name="chk_lessons_order"),
        CheckConstraint("duration_secs > 0", name="chk_lessons_duration_secs"),
    )

    chapter_id: Mapped[UUID] = mapped_column(ForeignKey(Chapter.id), nullable=False)
    title: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    order: Mapped[int] = mapped_column(type_=Integer(), nullable=False, default=1)
    video: Mapped[str | None] = mapped_column(type_=String(255), nullable=True)
    status: Mapped[LessonStatus] = mapped_column(
        type_=Enum(
            LessonStatus,
            name="lesson_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=LessonStatus.PENDING,
        server_default=LessonStatus.PENDING.value,
    )
    duration_secs: Mapped[int | None] = mapped_column(type_=Integer(), nullable=True)
    is_preview: Mapped[bool] = mapped_column(
        type_=Boolean(), nullable=False, default=False
    )
