from fastapi import APIRouter, HTTPException, status

from .. import schemas as schema
from ..crud import get_advertisement, save_advertisement, search_advertisements
from ..models import Advertisement
from .dependencies import SessionDependency

router = APIRouter(tags=["advertisement"])


@router.get(
    "/advertisement",
    response_model=list[schema.GetAdvertisementResponse],
    status_code=status.HTTP_200_OK,
)
async def search_advertisements_view(
    session: SessionDependency,
    title: str | None = None,
    description: str | None = None,
    author: str | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
):
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="price_min must be less than or equal to price_max",
        )
    return await search_advertisements(
        session=session,
        title=title,
        description=description,
        author=author,
        price_min=price_min,
        price_max=price_max,
    )


@router.get(
    "/advertisement/{advertisement_id}",
    response_model=schema.GetAdvertisementResponse,
    status_code=status.HTTP_200_OK,
)
async def get_advertisement_view(session: SessionDependency, advertisement_id: int):
    return await get_advertisement(session, advertisement_id)


@router.post(
    "/advertisement",
    response_model=schema.CreateAdvertisementResponse,
    summary="Create new advertisement item",
    status_code=status.HTTP_201_CREATED,
)
async def create_advertisement(
    advertisement_json: schema.CreateAdvertisementRequest,
    session: SessionDependency,
):
    advertisement = Advertisement(**advertisement_json.model_dump())
    advertisement = await save_advertisement(session, advertisement)
    return {"id": advertisement.id}


@router.patch(
    "/advertisement/{advertisement_id}",
    response_model=schema.UpdateAdvertisementResponse,
    status_code=status.HTTP_200_OK,
)
async def update_advertisement(
    advertisement_json: schema.UpdateAdvertisementRequest,
    session: SessionDependency,
    advertisement_id: int,
):
    advertisement = await get_advertisement(session, advertisement_id)
    advertisement_dict = advertisement_json.model_dump(exclude_unset=True)
    for field, value in advertisement_dict.items():
        setattr(advertisement, field, value)
    return await save_advertisement(session, advertisement)


@router.delete(
    "/advertisement/{advertisement_id}",
    response_model=schema.OkResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_advertisement(advertisement_id: int, session: SessionDependency):
    advertisement = await get_advertisement(session, advertisement_id)
    await session.delete(advertisement)
    await session.commit()
    return {"status": "ok"}
