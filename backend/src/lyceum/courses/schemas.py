from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from lyceum.courses.models import CourseLevel, CourseStatus


class CourseOrderBy(StrEnum):
    AVG_RATING = "avg_rating"
    RATING_COUNT = "rating_count"
    ENROLLMENT_COUNT = "enrollment_count"
    PUBLISHED_AT = "published_at"


class CourseFilterRequest(BaseModel):
    keyword: str | None = Field(default=None, min_length=1, max_length=200)

    instructor_id: UUID | None = None

    level: CourseLevel | None = None

    from_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    to_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )

    from_rating: int | None = Field(default=None, ge=0, le=5)
    to_rating: int | None = Field(default=None, ge=0, le=5)

    from_duration_mins: int | None = Field(default=None, ge=0)
    to_duration_mins: int | None = Field(default=None, ge=0)

    order_by: CourseOrderBy | None = None

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=50)

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        if (
            self.from_rating is not None
            and self.to_rating is not None
            and self.from_rating > self.to_rating
        ):
            raise ValueError("Khoảng điểm không hợp lệ")
        if (
            self.from_price is not None
            and self.to_price is not None
            and self.from_price > self.to_price
        ):
            raise ValueError("Khoảng giá không hợp lệ")
        if (
            self.from_duration_mins is not None
            and self.to_duration_mins is not None
            and self.from_duration_mins > self.to_duration_mins
        ):
            raise ValueError("Khoảng tổng thời lượng khóa học không hợp lệ")
        return self


@dataclass(frozen=True)
class CourseFilter:
    keyword: str | None = None
    instructor_id: UUID | None = None
    level: CourseLevel | None = None
    from_price: Decimal | None = None
    to_price: Decimal | None = None
    from_rating: int | None = None
    to_rating: int | None = None
    from_duration_mins: int | None = None
    to_duration_mins: int | None = None
    order_by: CourseOrderBy | None = None


class CourseListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    instructor_id: UUID
    instructor_name: str
    slug: str
    short_description: str | None
    thumbnail: str
    level: CourseLevel
    status: CourseStatus
    price: Decimal
    avg_rating: float | None
    rating_count: int
    enrollment_count: int
    total_duration_mins: int


type LearningPoint = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=1000,
        pattern=r"^[^\r\n]+$",
    ),
]


class CourseCreateRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(min_length=1, max_length=255)
    short_description: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: list[LearningPoint] = Field(
        min_length=1,
        max_length=50,
    )
    level: CourseLevel
    price: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2,
    )


class CourseCreateResponse(CourseListResponse):
    description: list[str]

    @field_validator("description", mode="before")
    @classmethod
    def deserialize_description(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return value.split("\n")
        return value
