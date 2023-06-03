from pydantic import BaseModel as BM
from pydantic import constr

from app.utils.constants import TIMEDELTA_REGEX


class BaseModel(BM):
    def dict(self, exclude_none: bool = True, **kwargs: dict) -> dict:
        return super().dict(exclude_none=exclude_none, **kwargs)


class ResponseCourierModel(BaseModel):
    """Модель курьера для ответа"""

    courier_id: int
    courier_type: str
    regions: list[int]
    working_hours: list[constr(regex=TIMEDELTA_REGEX)]


class ResponseCouriersModel(BaseModel):
    """Модель курьеров для ответа"""

    couriers: list[ResponseCourierModel]


class ResponseOrderModel(BaseModel):
    """Модель заказа для ответа"""

    order_id: int
    weight: float
    regions: int
    delivery_hours: list[constr(regex=TIMEDELTA_REGEX)]
    cost: int
    completed_time: str | None


class ResponseOrdersModel(BaseModel):
    orders: list[ResponseOrderModel]


class CourierStatsModel(BaseModel):
    """Модель статистики курьера"""

    courier_id: int
    courier_type: str
    regions: list[int]
    working_hours: list[constr(regex=TIMEDELTA_REGEX)]
    rating: int | None
    earnings: int | None
