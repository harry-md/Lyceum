from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.courses.models import Course
from lyceum.db.models import BaseModel


class Chapter(BaseModel):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("course_id", "order", name="uq_chapters_course_order"),
        CheckConstraint('"order" >= 1', name="chk_chapters_order"),
    )

    course_id: Mapped[UUID] = mapped_column(ForeignKey(Course.id), nullable=False)
    title: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    order: Mapped[int] = mapped_column(type_=Integer(), nullable=False, default=1)
