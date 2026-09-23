from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.db.models import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def find_by_id(self, id_: UUID) -> ModelT | None:
        return await self._session.get(self._model, id_)

    async def find_all(self) -> list[ModelT]:
        stm = select(self._model)
        res = await self._session.scalars(stm)
        return list(res.all())

    async def find_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        order_by: str | None = None,
    ) -> Page[ModelT]:
        offset = (page - 1) * page_size

        stm = select(self._model).limit(page_size).offset(offset)
        if order_by:
            col = getattr(self._model, order_by)
            stm = stm.order_by(col)
        else:
            stm = stm.order_by(self._model.id)

        result = await self._session.execute(stm)
        items = result.scalars().all()

        count_stm = select(func.count()).select_from(self._model)

        total = await self._session.scalar(count_stm) or 0

        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

        return Page(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def add(self, entity: ModelT) -> None:
        self._session.add(entity)

    async def delete(self, entity: ModelT) -> None:
        await self._session.delete(entity)
