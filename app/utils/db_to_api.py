from app.db.schema import Courier, Order
from app.models.response_models import ResponseCourierModel, ResponseOrderModel
from app.utils.time_converters import time_obj_to_str


def build_response_courier(db_courier: Courier) -> ResponseCourierModel:
    courier_worked_hours = [
        f'{i.start_time.strftime("%H:%M")}-{i.end_time.strftime("%H:%M")}' for i in db_courier.worked_hours
    ]
    return ResponseCourierModel(
        courier_id=db_courier.courier_id,
        courier_type=db_courier.courier_type,
        regions=[area.area_number for area in db_courier.areas],
        working_hours=courier_worked_hours,
    )


def build_response_order(db_order: Order) -> ResponseOrderModel:
    order_delivery_time = [f"{time_obj_to_str(i.start_time)}-{time_obj_to_str(i.end_time)}" for i in db_order.delivery_hours]
    return ResponseOrderModel(
        order_id=db_order.order_id,
        weight=db_order.weight,
        regions=db_order.area.area_number,
        delivery_hours=order_delivery_time,
        cost=db_order.cost,
        completed_time=db_order.completed_at
        if not db_order.completed_at
        else db_order.completed_at.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    ).dict(exclude_none=True)
