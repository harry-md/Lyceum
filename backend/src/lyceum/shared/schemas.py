from typing import Generic, TypeVar

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    msg: str


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
