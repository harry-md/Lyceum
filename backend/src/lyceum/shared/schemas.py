from typing import TypeVar

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    msg: str


T = TypeVar("T")


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
