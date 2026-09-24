from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.courses.models import Course
from lyceum.db.models import BaseModel
from lyceum.users.models import User


class EnrollmentStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


class Enrollment(BaseModel):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollments_user_course"),
        CheckConstraint("completed_at > enrolled_at", name="chk_completed_enrolled"),
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), nullable=False)
    course_id: Mapped[UUID] = mapped_column(
        ForeignKey(Course.id), nullable=False, index=True
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        type_=Enum(
            EnrollmentStatus,
            name="enrollment_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=EnrollmentStatus.ACTIVE,
        server_default=EnrollmentStatus.ACTIVE.value,
    )
    enrolled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
