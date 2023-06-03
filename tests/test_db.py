import logging

import pytest
from sqlalchemy import select

from app.db.schema import Courier, CourierType
from app.db.services.couriers_service import CourierService
from utils.data_generators.api_to_dto import api_models_to_dto
from utils.data_generators.generate_couriers import generate_couriers

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()


@pytest.mark.asyncio()
async def test_name_courier_types_is_valid(get_session):
    """Проверяю, что типы курьеров из базы совпадают с валидными типами"""
    valid_types = ["BIKE", "FOOT", "AUTO"]
    async with get_session() as session:
        stmt = select(CourierType)
        result = await session.execute(stmt)
        types_names = [type.type_id for type in result.scalars().all()]
        assert set(types_names) == set(valid_types)


@pytest.mark.asyncio()
async def test_count_courier_types(get_session):
    """Проверяю сколько типов курьеров лежит в базе, что это число совпадает с нужным"""
    async with get_session() as session:
        stmt = select(CourierType)
        result = await session.execute(stmt)
        assert len(result.scalars().all()) == 3


@pytest.mark.asyncio()
async def test_couriers_create(get_session):
    """Проверяю, что функция add_couriers добавляет ровно 100 курьеров"""
    api_couriers_generated = generate_couriers(100)
    dto_couriers = [api_models_to_dto(courier) for courier in api_couriers_generated.couriers]
    res = await CourierService.add_couriers(dto_couriers)
    assert len(res) == 100


@pytest.mark.asyncio()
async def test_valid_couriers_created_in_db(get_session):
    """Проверяю, что функця add_couriers не добавляет в базу невалидных курьеров"""
    api_couriers_generated = generate_couriers(100)
    dto_couriers = [api_models_to_dto(courier) for courier in api_couriers_generated.couriers]
    res = await CourierService.add_couriers(dto_couriers)
    async with get_session() as session:
        stmt = select(Courier)
        res = await session.execute(stmt)
        assert len(res.scalars().all()) == 100
