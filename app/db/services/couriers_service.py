from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert

from app.db.db_config import DB_DATA
from app.db.schema import Area, Courier, courier_area, CourierWorkTime
from app.db.utils import bulk_insert_by_parts, CourierStats
from app.models.dto import CourierDto
from app.utils.constants import MAX_COURIER_WORKING_HOUR_COUNT


class CourierService:
    @staticmethod
    async def add_couriers(new_couriers: list[CourierDto]) -> list[Courier] | bool:
        new_session = DB_DATA.session_factory()

        async with new_session() as session:
            all_types_query = text(
                """SELECT courier_type.id, courier_type.max_area
                        FROM courier_type"""
            )
            courier_types_cursor = await session.execute(all_types_query)
            possible_types = {courier_type[0]: courier_type[1] for courier_type in courier_types_cursor.all()}
            areas_to_add = []
            couriers_to_add = []
            for courier in new_couriers:
                request_valid_courier_type = possible_types.get(courier.courier_type)
                if not request_valid_courier_type or len(courier.regions) > request_valid_courier_type:
                    return False
                areas_to_add.extend([{"area_number": area} for area in courier.regions])
                couriers_to_add.append({"courier_type": courier.courier_type})

            add_couriers_query = insert(Courier).values(couriers_to_add).returning(Courier.courier_id)
            added_couriers_cursor = await session.execute(add_couriers_query)
            added_couriers_id = added_couriers_cursor.scalars().all()

            add_areas_query = insert(Area).values(areas_to_add).on_conflict_do_nothing(index_elements=["area_number"])
            await session.execute(add_areas_query)
            await session.commit()
            unique_areas_number = {v for dict_obj in areas_to_add for v in dict_obj.values()}
            select_areas_query = text("SELECT area_id, area_number FROM area WHERE area_number = ANY(:id_array)")
            select_areas_cursor = await session.execute(select_areas_query, {"id_array": unique_areas_number})
            area_id_by_area_number = {area[1]: area[0] for area in select_areas_cursor.all()}

            mapped_couriers_areas = []
            mapped_couriers_working_hours = []
            for i, courier in enumerate(new_couriers):
                for area_number in courier.regions:
                    new_area_courier_pair = {
                        "courier_id": added_couriers_id[i],
                        "area_id": area_id_by_area_number[area_number],
                    }
                    mapped_couriers_areas.append(new_area_courier_pair)

                for hour_delta in courier.working_hours:
                    start_time, end_time = hour_delta.split("-")
                    start_time = datetime.strptime(start_time, "%H:%M")
                    end_time = datetime.strptime(end_time, "%H:%M")
                    new_working_hours = {"courier_id": added_couriers_id[i], "start_at": start_time, "end_at": end_time}
                    mapped_couriers_working_hours.append(new_working_hours)

            await bulk_insert_by_parts(
                session=session,
                model=CourierWorkTime,
                partitision_size=MAX_COURIER_WORKING_HOUR_COUNT,
                batch=mapped_couriers_working_hours,
            )
            await bulk_insert_by_parts(
                session=session,
                model=courier_area,
                partitision_size=16383,
                batch=mapped_couriers_areas,
            )
            return added_couriers_id

    @staticmethod
    async def get_courier_by_id(courier_id: int) -> bool | Courier:
        new_session = DB_DATA.session_factory()
        async with new_session() as session:
            db_courier = await session.get(Courier, courier_id)
            return db_courier if db_courier else None

    @staticmethod
    async def get_couries_with_pagination(limit: int, offset: int) -> list[Courier]:
        new_session = DB_DATA.session_factory()
        async with new_session() as session:
            get_couriers_query = select(Courier).offset(offset).limit(limit).order_by(Courier.courier_id)
            res = await session.execute(get_couriers_query)
            return res.scalars().all()

    @staticmethod
    async def get_courier_stats(courier_id: int, start_date: datetime, end_date: datetime) -> Courier:
        new_session = DB_DATA.session_factory()
        async with new_session() as session:
            db_courier = await session.get(Courier, courier_id)
            if not db_courier:
                return None
            stats_query = text(
                """
                SELECT "courier".courier_id,
                    (COUNT("order".order_id) / NULLIF(((EXTRACT(EPOCH FROM  :end_date ::timestamp) -
                            EXTRACT(EPOCH FROM :start_date ::timestamp)) / 3600), 0)
                    * MAX("courier_type".rating_coefficient)) as coefficient,
                MAX("courier_type".salary_coefficient) * SUM("order".cost) AS total_salary
                FROM "courier"
                LEFT JOIN
                    (SELECT order_id, courier, cost from "order"
                        WHERE "order".completed_time >= :start_date
                            AND "order".completed_time < :end_date)
                    "order"
                    ON "courier".courier_id = "order".courier
                LEFT JOIN "courier_type"
                    ON "courier_type".id = "courier".courier_type
                    WHERE "courier".courier_id = :courier_id
                GROUP BY "courier".courier_id
           """
            )
            stats_coursor = await session.execute(
                stats_query,
                {
                    "courier_id": courier_id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            stats_res = CourierStats(*stats_coursor.all()[0])
            return {"courier": db_courier, "salary": stats_res.salary, "rating": stats_res.rating}
