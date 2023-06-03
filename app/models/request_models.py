# noqa:TC003
from datetime import datetime

from pydantic import BaseModel, constr, Field, StrictInt, validator

from app.utils.constants import TIMEDELTA_REGEX


def max_value_validator(number: int) -> int:
    """validate, that input value less than max int32"""
    if number > 2147483647:
        raise ValueError("max int32 value is 2147483647")
    return number


class OrderRequestModel(BaseModel):
    """Модель нового заказа"""

    weight: float
    regions: StrictInt
    delivery_hours: list[constr(regex=TIMEDELTA_REGEX)]
    cost: int

    int_value_is_valid = validator("regions", "cost", allow_reuse=True)(max_value_validator)

    @validator("weight", "cost")
    def validate_weight(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("weight must be positive float")
        return value

    @validator("regions")
    def validate_region(cls, value: int | float) -> int:
        if value <= 0:
            raise ValueError("regions must be positive int")
        return value

    @validator("delivery_hours")
    def validate_delivery_hours_not_empty(cls, value: list[str]) -> list[str]:
        if value == []:
            raise ValueError("delivery_hours mustnt empty")
        return value


class AddOrdersModel(BaseModel):
    """модель импорта заказов в post /orders"""

    orders: list[OrderRequestModel]


class PaginationModel(BaseModel):
    """Модель пагинации, с установленными дефолтами по условию тз"""

    limit: int = Field(ge=1, le=2147483647, default=1)
    offset: int = Field(ge=0, le=2147483647, default=0)


class CourierRequestModel(BaseModel):
    """Модель нового курьера"""

    courier_type: str
    regions: list[StrictInt]
    working_hours: list[constr(regex=TIMEDELTA_REGEX)]

    @validator("regions")
    def validate_all_regions(value: list[int]) -> list[int]:
        for region_number in value:
            if region_number > 2147483647:
                raise ValueError("max int32 value is 2147483647")
        if len(value) != len(set(value)):
            raise ValueError("Regions dont repeat")
        return value

    @validator("working_hours")
    def validate_delivery_hours_not_empty(cls, value: list[str]) -> list[str]:
        if value == []:
            raise ValueError("delivery_hours mustnt empty")
        return value


class AddCouriersModel(BaseModel):
    """модель импорта курьеров в post /couriers"""

    couriers: list[CourierRequestModel]


class OrderCompleteModel(BaseModel):
    """Api модель подтверждения заказа"""

    order_id: StrictInt
    courier_id: StrictInt
    complete_time: str

    int_value_is_valid = validator("order_id", "courier_id", allow_reuse=True)(max_value_validator)

    @validator("order_id", "courier_id")
    def validate_id_is_valid(value: int) -> int:
        if value <= 0:
            raise ValueError("Id must be positive integer")
        return value

    @validator("complete_time")
    def validate_date_format(value: str) -> str:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")


class OrdersCompleteModel(BaseModel):
    """Модель списка заказов для подтверждения"""

    complete_info: list[OrderCompleteModel]
