from collections.abc import Sequence
from dataclasses import dataclass
from typing import Generic, TypeVar
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

    async def find_all_paginated(
        self,
        offset: int = 0,
        limit: int | None = None,
    ) -> list[ModelT]:
        stmt = select(self._model).offset(offset)

        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self._session.scalars(stmt)
        return list(result.all())

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self._model)
        return await self._session.scalar(stmt) or 0

    def add(self, entity: ModelT) -> None:
        self._session.add(entity)

    async def delete(self, entity: ModelT) -> None:
        await self._session.delete(entity)
