from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.courses.models import Course
from lyceum.db.models import BaseModel
from lyceum.users.models import User


class Review(BaseModel):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("course_id", "user_id", name="uq_reviews_user_course"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="chk_reviews_rating"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), nullable=False)
    course_id: Mapped[UUID] = mapped_column(ForeignKey(Course.id), nullable=False)
    rating: Mapped[int] = mapped_column(type_=Integer(), nullable=False)
    comment: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
