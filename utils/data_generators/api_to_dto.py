from typing import TypeAlias, Union

from app.models.dto import CourierDto, OrderDto
from app.models.request_models import CourierRequestModel, OrderRequestModel

ApiModel: TypeAlias = Union[OrderRequestModel, CourierRequestModel]


def api_models_to_dto(model: ApiModel) -> Union[CourierDto, OrderDto]:
    """Returned dto obj from api model obj, use for tesing"""
    model_class = type(model)
    if model_class == CourierRequestModel:
        return CourierDto(**model.dict())
    elif model_class == OrderRequestModel:
        return OrderDto(**model.dict())
