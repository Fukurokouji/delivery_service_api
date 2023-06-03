from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse
from starlette import status
from typing_extensions import Annotated

from app.db.services.orders_service import OrdersService
from app.models.dto import CompleteOrderDto, OrderDto
from app.models.request_models import AddOrdersModel, OrdersCompleteModel, PaginationModel
from app.models.response_models import ResponseOrderModel, ResponseOrdersModel
from app.utils.db_to_api import build_response_order
from app.utils.rps_limiter import limiter

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def get_orders(request: Request, pagination: PaginationModel = Depends()) -> str:
    retrieved_db_orders = await OrdersService.get_orders_with_pagination(**pagination.dict())
    orders_response = ResponseOrdersModel(orders=[build_response_order(db_order) for db_order in retrieved_db_orders]).dict()
    orders_response["limit"] = pagination.limit
    orders_response["offset"] = pagination.offset
    return JSONResponse(content=orders_response, status_code=status.HTTP_200_OK)


@router.post("", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def post_orders(request: Request, orders: AddOrdersModel) -> str:
    dto_orders = [OrderDto(**api_order.dict()) for api_order in orders.orders]
    retrieved_orders_id = await OrdersService.add_orders(dto_orders)
    orders_response = []
    for num, order in enumerate(orders.orders):
        new_order = ResponseOrderModel(order_id=retrieved_orders_id[num][0], **order.dict(), completed_time=None)
        orders_response.append(new_order.dict())
    return JSONResponse(content=orders_response, status_code=status.HTTP_200_OK)


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def get_order_by_id(request: Request, order_id: Annotated[int, Path(title="Order ID", le=2147483647, gt=0)]) -> str:
    retrieved_db_order = await OrdersService.get_order_by_id(order_id=order_id)
    if not retrieved_db_order:
        return JSONResponse(content={"message": "error, not found"}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(content=build_response_order(db_order=retrieved_db_order), status_code=status.HTTP_200_OK)


@router.post("/complete", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def complete_order(request: Request, completed_orders: OrdersCompleteModel) -> str:
    dto_completes = [CompleteOrderDto(**api_complete.dict()) for api_complete in completed_orders.complete_info]
    retrieved_orders_complete = await OrdersService.complete_orders(dto_completes)
    if retrieved_orders_complete is None:
        return JSONResponse(content={"message": "error, not found"}, status_code=status.HTTP_404_NOT_FOUND)
    if retrieved_orders_complete is False:
        return JSONResponse(content={"message": "order match with another courier"}, status_code=status.HTTP_400_BAD_REQUEST)
    orders_response = []
    for db_order in retrieved_orders_complete:
        response_order = build_response_order(db_order)
        orders_response.append(response_order)
    return JSONResponse(content=orders_response, status_code=status.HTTP_200_OK)
