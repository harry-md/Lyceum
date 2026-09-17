from typing import Generic, List, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lyceum.db.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def find_by_id(self, id_: UUID) -> ModelT | None:
        return await self._session.get(self._model, id_)

    async def find_all(self) -> List[ModelT]:
        result = await self._session.scalars(select(self._model))
        return list(result.all())

    def add(self, entity: ModelT) -> None:
        self._session.add(entity)

    async def delete(self, entity: ModelT) -> None:
        await self._session.delete(entity)
