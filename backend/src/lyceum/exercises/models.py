from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from lyceum.chapters.models import Chapter
from lyceum.db.models import BaseModel
from lyceum.users.models import Instructor, User


class ExerciseStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Exercise(BaseModel):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("chapter_id", "order", name="uq_exercises_chapter_order"),
        CheckConstraint('"order" >= 1', name="chk_exercises_order"),
        CheckConstraint(
            "pass_score_percent >= 0 AND pass_score_percent <= 100",
            name="chk_exercises_pass_score_percent",
        ),
        CheckConstraint("max_attempts >= 1", name="chk_exercises_max_attempts"),
        CheckConstraint("time_limit_mins >= 1", name="chk_exercises_time_limit_mins"),
    )

    chapter_id: Mapped[UUID] = mapped_column(ForeignKey(Chapter.id), nullable=False)
    title: Mapped[str] = mapped_column(type_=String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    order: Mapped[int] = mapped_column(type_=Integer(), nullable=False, default=1)
    status: Mapped[ExerciseStatus] = mapped_column(
        type_=Enum(
            ExerciseStatus,
            name="exercise_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=ExerciseStatus.DRAFT,
        server_default=ExerciseStatus.DRAFT.value,
    )
    max_attempts: Mapped[int | None] = mapped_column(type_=Integer(), nullable=True)
    time_limit_mins: Mapped[int | None] = mapped_column(type_=Integer(), nullable=True)
    pass_score_percent: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=5, scale=2), nullable=False, default=50.00
    )


class QuestionType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    ESSAY = "essay"


class Question(BaseModel):
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("exercise_id", "order", name="uq_questions_exercise_order"),
        CheckConstraint('"order" >= 1', name="chk_questions_order"),
        CheckConstraint("points >= 0", name="chk_questions_points"),
    )

    exercise_id: Mapped[UUID] = mapped_column(ForeignKey(Exercise.id), nullable=False)
    type: Mapped[QuestionType] = mapped_column(
        Enum(
            QuestionType,
            name="type",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=QuestionType.SINGLE_CHOICE,
        server_default=QuestionType.SINGLE_CHOICE.value,
    )
    content: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    order: Mapped[int] = mapped_column(type_=Integer(), nullable=False, default=1)
    points: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=5, scale=2), nullable=False, default=0.00
    )


class ExerciseAttemptStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class ExerciseAttempt(BaseModel):
    __tablename__ = "exercise_attempts"
    __table_args__ = (
        UniqueConstraint(
            "exercise_id",
            "user_id",
            "attempt_number",
            name="uq_exercise_attempts_user_exercise",
        ),
        CheckConstraint(
            "pass_score_percent >= 0 AND pass_score_percent <= 100",
            name="chk_exercise_attempts_pass_score_percent",
        ),
        CheckConstraint("score >= 0", name="chk_exercise_attempts_score"),
        CheckConstraint(
            "attempt_number >= 1", name="chk_exercise_attempts_attempt_number"
        ),
    )

    exercise_id: Mapped[UUID] = mapped_column(ForeignKey(Exercise.id), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), nullable=False)
    attempt_number: Mapped[int] = mapped_column(type_=Integer(), nullable=False)
    status: Mapped[ExerciseAttemptStatus] = mapped_column(
        type_=Enum(
            ExerciseAttemptStatus,
            name="exercise_attempt_status",
            values_callable=lambda enum_class: [member.value for member in enum_class],
            validate_strings=True,
        ),
        nullable=False,
        default=ExerciseAttemptStatus.IN_PROGRESS,
        server_default=ExerciseAttemptStatus.IN_PROGRESS.value,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        type_=DateTime(timezone=True), nullable=True
    )
    score: Mapped[Decimal | None] = mapped_column(
        type_=Numeric(precision=5, scale=2), nullable=True
    )
    pass_score_percent: Mapped[Decimal] = mapped_column(
        type_=Numeric(precision=5, scale=2), nullable=False, default=50.00
    )


class QuestionAnswer(BaseModel):
    __tablename__ = "question_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id", "question_id", name="uq_question_answers_attempt_question"
        ),
    )

    question_id: Mapped[UUID] = mapped_column(ForeignKey(Question.id), nullable=False)
    attempt_id: Mapped[UUID] = mapped_column(
        ForeignKey(ExerciseAttempt.id), nullable=False
    )
    answer_text: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    earned_point: Mapped[Decimal | None] = mapped_column(
        type_=Numeric(precision=5, scale=2), nullable=True
    )
    feedback: Mapped[str | None] = mapped_column(type_=Text(), nullable=True)
    graded_by: Mapped[UUID | None] = mapped_column(
        ForeignKey(Instructor.user_id), nullable=True
    )


class Choice(BaseModel):
    __tablename__ = "choices"
    __table_args__ = (
        UniqueConstraint("question_id", "order", name="uq_choices_question_order"),
        CheckConstraint('"order" >= 1', name="chk_choices_order"),
    )

    question_id: Mapped[UUID] = mapped_column(ForeignKey(Question.id), nullable=False)
    content: Mapped[str] = mapped_column(type_=Text(), nullable=False)
    order: Mapped[int] = mapped_column(type_=Integer(), nullable=False, default=1)
    is_correct: Mapped[bool] = mapped_column(
        type_=Boolean(), nullable=False, default=False
    )


answer_choices = Table(
    "answer_choices",
    BaseModel.metadata,
    Column("answer_id", ForeignKey(QuestionAnswer.id), primary_key=True),
    Column("choice_id", ForeignKey(Choice.id), primary_key=True),
)
