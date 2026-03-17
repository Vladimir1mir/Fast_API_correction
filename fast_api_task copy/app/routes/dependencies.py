from fastapi import Depends
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import SessionFactory


async def get_db_session() -> AsyncSession:
    async with SessionFactory() as session:
        yield session

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
