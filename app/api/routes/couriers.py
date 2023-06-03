from datetime import datetime

from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse
from starlette import status
from typing_extensions import Annotated

from app.db.services.couriers_service import CourierService
from app.models.dto import CourierDto
from app.models.request_models import AddCouriersModel, PaginationModel
from app.models.response_models import CourierStatsModel, ResponseCourierModel, ResponseCouriersModel
from app.utils.db_to_api import build_response_courier
from app.utils.rps_limiter import limiter

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def get_couriers(request: Request, pagination: PaginationModel = Depends()) -> str:
    db_retrieved_couriers = await CourierService.get_couries_with_pagination(**pagination.dict())
    response_couriers = [build_response_courier(courier) for courier in db_retrieved_couriers]
    response_data = ResponseCouriersModel(
        couriers=response_couriers,
    ).dict()
    response_data["limit"] = pagination.limit
    response_data["offset"] = pagination.offset
    return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)


@router.post("", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def post_couriers(request: Request, couriers: AddCouriersModel) -> JSONResponse:
    dto_couriers = [CourierDto(**api_courier.dict()) for api_courier in couriers.couriers]
    retrieved_couriers_id = await CourierService.add_couriers(dto_couriers)
    if not retrieved_couriers_id:
        return JSONResponse(content={"status": "error"}, status_code=status.HTTP_400_BAD_REQUEST)
    response_couriers = []
    for num, order in enumerate(couriers.couriers):
        new_order = ResponseCourierModel(courier_id=retrieved_couriers_id[num], **order.dict(), completed_time=None)
        response_couriers.append(new_order.dict())
    return JSONResponse(content=ResponseCouriersModel(couriers=response_couriers).dict(), status_code=status.HTTP_200_OK)


@router.get("/{courier_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def get_courier_by_id(
    request: Request, courier_id: Annotated[int, Path(title="Courier ID", le=2147483647, gt=0)]
) -> JSONResponse:
    got_db_courier = await CourierService.get_courier_by_id(courier_id=courier_id)
    if not got_db_courier:
        return JSONResponse(content={"status": "error"}, status_code=status.HTTP_404_NOT_FOUND)
    answer_courier = build_response_courier(got_db_courier)
    return JSONResponse(content=answer_courier.dict(), status_code=status.HTTP_200_OK)


@router.get("/meta-info/{courier_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/seconds")
async def get_courier_info(
    request: Request,
    courier_id: Annotated[int, Path(title="Courier ID", le=2147483647, gt=0)],
    startDate: str,
    endDate: str,
) -> JSONResponse:
    try:
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
        end_date = datetime.strptime(endDate, "%Y-%m-%d")
    except ValueError:
        return JSONResponse(content={"status": "error"}, status_code=status.HTTP_400_BAD_REQUEST)
    if start_date >= end_date:
        return JSONResponse(content={"status": "error"}, status_code=status.HTTP_400_BAD_REQUEST)
    db_response = await CourierService.get_courier_stats(
        courier_id=courier_id,
        start_date=start_date,
        end_date=end_date,
    )
    if not db_response:
        return JSONResponse(content={"status": "error"}, status_code=status.HTTP_404_NOT_FOUND)
    base_courier = build_response_courier(db_courier=db_response["courier"])
    answer_courier = CourierStatsModel(
        **base_courier.dict(),
        earnings=db_response["salary"],
        rating=db_response["rating"] if db_response["rating"] else None,
    )
    return JSONResponse(content=answer_courier.dict(), status_code=status.HTTP_200_OK)
