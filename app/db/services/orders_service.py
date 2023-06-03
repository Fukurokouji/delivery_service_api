from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.db.db_config import DB_DATA
from app.db.schema import Area, Order, OrderDeliveryHour
from app.db.utils import bulk_insert_by_parts
from app.models.dto import CompleteOrderDto, OrderDto
from app.utils.constants import MAX_DELIVERY_TIME_ORDER_COUNT, MAX_ORDER_COUNT
from app.utils.time_converters import str_to_time_obj


class OrdersService:
    @staticmethod
    async def add_orders(orders: list[OrderDto]) -> list[Order]:
        new_session = DB_DATA.session_factory()

        async with new_session() as session:
            orders_to_add = []
            areas_to_add = []
            orders_for_answ = []

            for order in orders:
                orders_for_answ.append(order)
                areas_to_add.append({"area_number": order.regions})
                orders_to_add.append({"cost": order.cost, "weight": order.weight, "region": None})

            insert_or_ignore_areas_query = (
                insert(Area).values(areas_to_add).on_conflict_do_nothing(index_elements=["area_number"])
            )
            await session.execute(insert_or_ignore_areas_query)
            await session.commit()

            unique_areas_number = {area_number for area_dict in areas_to_add for area_number in area_dict.values()}
            get_areas_by_number_query = text("SELECT area_id, area_number FROM area WHERE area_number = ANY(:id_array)")
            get_areas_by_number_cursor = await session.execute(get_areas_by_number_query, {"id_array": unique_areas_number})
            get_areas_by_number_res = get_areas_by_number_cursor.all()

            area_id_by_area_number = {area[1]: area[0] for area in get_areas_by_number_res}
            for i, order in enumerate(orders_to_add):
                order["region"] = area_id_by_area_number[orders[i].regions]

            add_orders_res = await bulk_insert_by_parts(
                session=session,
                model=Order,
                partitision_size=MAX_ORDER_COUNT,
                batch=orders_to_add,
                returning=Order.order_id,
            )
            await session.commit()
            mapped_order_delivery_hours = []
            for i, order_data in enumerate(orders_for_answ):
                for hour_delta in order_data.delivery_hours:
                    start_time, end_time = hour_delta.split("-")
                    new_working_hours = {
                        "order_id": add_orders_res[i][0],
                        "start_at": str_to_time_obj(start_time),
                        "end_at": str_to_time_obj(end_time),
                    }
                    mapped_order_delivery_hours.append(new_working_hours)
            await bulk_insert_by_parts(
                session=session,
                model=OrderDeliveryHour,
                partitision_size=MAX_DELIVERY_TIME_ORDER_COUNT,
                batch=mapped_order_delivery_hours,
            )
            return add_orders_res

    @staticmethod
    async def get_order_by_id(order_id: int) -> Order | None:
        new_session = DB_DATA.session_factory()
        async with new_session() as session:
            db_order = await session.get(Order, order_id)
            if not db_order:
                return None
            return db_order

    @staticmethod
    async def get_orders_with_pagination(limit: int, offset: int) -> list[Order]:
        new_session = DB_DATA.session_factory()

        async with new_session() as session:
            get_orders_query = select(Order).offset(offset).limit(limit).order_by(Order.order_id)
            get_orders_cursor = await session.execute(get_orders_query)
            return get_orders_cursor.scalars().all()

    @staticmethod
    async def complete_orders(completes: list[CompleteOrderDto]) -> list[Order]:
        """
        Функция подтверждения заказов, работает по схеме:
        получаем курьеров, которые пришли на вставку,
        если кол-во в базе не совпадает с кол-вом данных - есть несуществуюший курьер.
        Потом проверяю, что в одной вставке нету двух одинаковых заказов.
        Также есть проверка, что если распределенный курьер на совпадает с тем,
        что пришел на вставке - невалидный кейс
        """
        new_session = DB_DATA.session_factory()
        async with new_session() as session:
            couriers_id = []
            orders_id = []
            orders_data = {}
            for complete_pair in completes:
                couriers_id.append(complete_pair.courier_id)
                orders_id.append(complete_pair.order_id)
                orders_data[complete_pair.order_id] = {
                    "courier": complete_pair.courier_id,
                    "time": complete_pair.complete_time,
                }
            unique_courier_id = set(couriers_id)
            unique_order_id = set(orders_id)
            courier_query = text("SELECT courier_id FROM courier WHERE courier_id = ANY(:id_array)")
            couriers_cursor = await session.execute(courier_query, {"id_array": unique_courier_id})
            couriers_res = couriers_cursor.all()
            if len((couriers_res)) != len(unique_courier_id):
                return None
            db_orders_query = select(Order).where(Order.order_id.in_(unique_order_id))
            db_orders_cursor = await session.execute(db_orders_query)
            db_orders_res = db_orders_cursor.scalars().all()
            if len(db_orders_res) != len(unique_order_id):
                return None
            for order in db_orders_res:
                current_order_details = orders_data[order.order_id]
                if order.courier and (order.courier != current_order_details["courier"]):
                    return False
                if not order.completed_at:
                    order.courier = current_order_details["courier"]
                    val_time = current_order_details["time"]
                    order.completed_at = val_time
            await session.commit()
            return db_orders_res
