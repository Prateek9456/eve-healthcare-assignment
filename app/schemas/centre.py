from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class TestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    created_at: datetime


class CentreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    location: str = Field(min_length=2, max_length=500)
    tests: list[TestCreate] = Field(min_length=1)


class CentreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    tests: list[TestResponse]
    created_at: datetime


class PaginatedCentresResponse(BaseModel):
    items: list[CentreResponse]
    total: int
    page: int
    page_size: int
