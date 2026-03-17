import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_not_blank(value: str | None) -> str | None:
    if value is None:
        return value
    if not value.strip():
        raise ValueError("must not be blank")
    return value


class OkResponse(BaseModel):
    status: Literal["ok"]


class AdvertisementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    price: int
    author: str
    date_of_creation: datetime.datetime


class GetAdvertisementResponse(AdvertisementResponse):
    pass


class CreateAdvertisementRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    price: int = Field(ge=0)
    author: str = Field(min_length=1)

    _validate_not_blank = field_validator(
        "title",
        "description",
        "author",
    )(validate_not_blank)


class CreateAdvertisementResponse(BaseModel):
    id: int


class UpdateAdvertisementRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = Field(default=None, min_length=1)
    price: int | None = Field(default=None, ge=0)
    author: str | None = Field(default=None, min_length=1)

    _validate_not_blank = field_validator(
        "title",
        "description",
        "author",
    )(validate_not_blank)


class UpdateAdvertisementResponse(AdvertisementResponse):
    pass
