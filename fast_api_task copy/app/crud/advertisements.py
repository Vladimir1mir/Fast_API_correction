from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Advertisement


async def save_advertisement(session: AsyncSession, advertisement: Advertisement):
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError as err:
        await session.rollback()
        if getattr(err.orig, "pgcode", None) == "23505":
            raise HTTPException(status_code=409, detail="Item already exist")
        raise
    await session.refresh(advertisement)
    return advertisement


async def get_advertisement(session: AsyncSession, advertisement_id: int):
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return advertisement


async def search_advertisements(
    session: AsyncSession,
    title: str | None = None,
    description: str | None = None,
    author: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
):
    query = select(Advertisement)

    if title:
        query = query.where(Advertisement.title.ilike(f"%{title}%"))
    if description:
        query = query.where(Advertisement.description.ilike(f"%{description}%"))
    if author:
        query = query.where(Advertisement.author.ilike(f"%{author}%"))
    if price_min is not None:
        query = query.where(Advertisement.price >= price_min)
    if price_max is not None:
        query = query.where(Advertisement.price <= price_max)

    result = await session.execute(query.order_by(Advertisement.id))
    return result.scalars().all()
