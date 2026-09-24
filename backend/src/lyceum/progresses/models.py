from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.db.models import BaseModel
from lyceum.lessons.models import Lesson
from lyceum.users.models import User


class LessonProgress(BaseModel):
    __tablename__ = "lesson_progresses"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id"),
        CheckConstraint(
            "last_watched_secs >= 0", name="chk_lesson_progresses_watched_secs"
        ),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), nullable=False)
    lesson_id: Mapped[UUID] = mapped_column(ForeignKey(Lesson.id), nullable=False)
    last_watched_secs: Mapped[int] = mapped_column(
        type_=Integer(), nullable=False, default=0
    )
    is_completed: Mapped[bool] = mapped_column(
        type_=Boolean(), nullable=False, default=False
    )
