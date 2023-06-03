import pytest
from sqlalchemy import select
from starlette import status

from app.db.schema import Courier, Order
from app.db.services.couriers_service import CourierService
from app.db.services.orders_service import OrdersService
from utils.data_generators.api_to_dto import api_models_to_dto
from utils.data_generators.generate_couriers import generate_couriers
from utils.data_generators.generate_orders import generate_valid_orders


@pytest.mark.asyncio()
@pytest.mark.parametrize("weight", ["str", -1, 0])
async def test_invalid_weight_in_post_orders(client, weight):
    json_orders = {"orders": [{"weight": weight, "regions": 1, "delivery_hours": ["10:00-13:00"], "cost": 1000}]}
    response = client.post("/orders", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("regions", [[1, 2], "str", 32.3, -1, -32.5, 0, 12345678900000])
async def test_invalid_regions_in_post_orders(client, regions):
    json_orders = {"orders": [{"weight": 0.234, "regions": regions, "delivery_hours": ["10:00-13:00"], "cost": 1000}]}
    response = client.post("/orders", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("delivery_hours", [[1, 2], [0, 0], ["10-00-13-00"], ["st:r-s:tr"], ["str-str"]])
async def test_invalid_delivery_hours_in_post_orders(client, delivery_hours):
    json_orders = {"orders": [{"weight": 0.234, "regions": 1, "delivery_hours": delivery_hours, "cost": 1000}]}
    response = client.post("/orders", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("price", [0, -2, -2.0, "not price", 12345678900000])
async def test_invalid_price_in_post_orders(client, price):
    json_orders = {"orders": [{"weight": 1.799, "regions": 1, "delivery_hours": ["10:00-13:00"], "cost": price}]}
    response = client.post("/orders", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_post_valid_orders_request(client):
    json_orders = {"orders": [{"weight": 1.799, "regions": 1, "delivery_hours": ["10:00-13:00"], "cost": 1000}]}
    response = client.post("/orders", json=json_orders)
    assert response.status_code == status.HTTP_200_OK
    response_order = response.json()[0]
    assert response_order["weight"] == 1.799
    assert response_order["regions"] == 1
    assert response_order["cost"] == 1000


@pytest.mark.asyncio()
async def test_post_orders_create_orders(client, get_session):
    json_orders = {"orders": [{"weight": 1.799, "regions": 1, "delivery_hours": ["10:00-13:00"], "cost": 1000}]}
    response = client.post("/orders", json=json_orders)
    response_order = response.json()[0]
    async with get_session() as session:
        db_orders_query = select(Order)
        db_ordes_cursor = await session.execute(db_orders_query)
        db_orders_res = db_ordes_cursor.scalars().all()
        db_added_order = db_orders_res[0]
        assert len(db_orders_res) == 1
        assert db_added_order.cost == response_order["cost"]
        assert db_added_order.region == response_order["regions"]
        assert db_added_order.weight == response_order["weight"]
        assert db_added_order.completed_at is None


@pytest.mark.asyncio()
async def test_10k_post_orders(client, get_session):
    orders = generate_valid_orders(10000)
    api_orders = [order.dict() for order in orders]
    response = client.post("/orders", json={"orders": api_orders})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10000
    async with get_session() as session:
        db_orders_query = select(Order)
        db_ordes_cursor = await session.execute(db_orders_query)
        db_orders_res = db_ordes_cursor.scalars().all()
        assert len(db_orders_res) == 10000


@pytest.mark.asyncio()
@pytest.mark.parametrize("order_id", [-1, 3.22, 0, True, "asdasd", 12345678900000])
async def test_invalid_order_id_get_orders_by_id(client, order_id):
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_get_dont_exist_order_by_id(client):
    response = client.get("/orders/1337")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_exist_order(client):
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    response = client.get("/orders/1").json()
    assert response["order_id"] == 1
    assert response["weight"] == orders[0].dict()["weight"]
    assert response["regions"] == orders[0].dict()["regions"]
    assert response["cost"] == orders[0].dict()["cost"]
    assert response["delivery_hours"] == orders[0].dict()["delivery_hours"]


@pytest.mark.asyncio()
async def test_get_orders_without_params(client):
    response = client.get("/orders")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
@pytest.mark.parametrize("limit", [-1, 12.2, "string", 0, 12345678900000])
async def test_get_orders_with_invalid_limit(client, limit):
    response = client.get("/orders", params={"limit": limit})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("offset", [-1, "sadadas", -3.22, 14.5])
async def test_get_orders_with_invalid_offset(client, offset):
    response = client.get("/orders", params={"offset": offset})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_get_orders_1_order(client):
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    response = client.get("/orders")
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data["orders"]) == 1
    response_order = response_data["orders"][0]
    assert response_order["weight"] == orders[0].dict()["weight"]
    assert response_order["regions"] == orders[0].dict()["regions"]
    assert response_order["cost"] == orders[0].dict()["cost"]


@pytest.mark.asyncio()
async def test_get_orders_2_order(client):
    orders = generate_valid_orders(100)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    response = client.get("/orders", params={"limit": 2})
    response_data = response.json()["orders"]
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data) == 2
    first_response_order = response_data[0]
    assert first_response_order["weight"] == orders[0].dict()["weight"]
    assert first_response_order["regions"] == orders[0].dict()["regions"]
    assert first_response_order["cost"] == orders[0].dict()["cost"]
    second_response_order = response_data[1]
    assert second_response_order["weight"] == orders[1].dict()["weight"]
    assert second_response_order["regions"] == orders[1].dict()["regions"]
    assert second_response_order["cost"] == orders[1].dict()["cost"]


@pytest.mark.asyncio()
async def test_get_orders_2_order_with_offset(client):
    orders = generate_valid_orders(100)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    response = client.get("/orders", params={"offset": 1})
    response_data = response.json()["orders"]
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data) == 1
    first_response_order = response_data[0]
    assert first_response_order["weight"] == orders[1].dict()["weight"]
    assert first_response_order["regions"] == orders[1].dict()["regions"]
    assert first_response_order["cost"] == orders[1].dict()["cost"]


@pytest.mark.asyncio()
@pytest.mark.parametrize("order_id", [-1, 0, 14.1, "str", True, 12345678900000])
async def test_complete_order_with_invalid_order_id(client, order_id):
    couriers = generate_couriers(1)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    body = {"complete_info": [{"courier_id": 1, "order_id": order_id, "complete_time": "2023-04-28T17:10:08.554Z"}]}
    await CourierService.add_couriers(dto_couriers)
    response = client.post("/orders/complete", json=body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_id", [-1, 0, 14.1, "str", True, 12345678900000])
async def test_complete_order_with_invalid_courier_id(client, courier_id):
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    body = {"complete_info": [{"courier_id": courier_id, "order_id": 1, "complete_time": "2023-04-28T17:10:08.554Z"}]}
    response = client.post("/orders/complete", json=body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_complete_non_exist_order(client):
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    body = {"complete_info": [{"courier_id": 1, "order_id": 1, "complete_time": "2023-04-28T17:10:08.554Z"}]}
    response = client.post("/orders/complete", json=body)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "complete_time", [1, "adasdsa", -1, 2.3, "2023-04-28T17:10:08", "2023-0428T17:10:08.554Z", "2023-04-28T17:10.554Z"]
)
async def test_complete_order_with_invalid_complete_time(client, complete_time):
    couriers = generate_couriers(1)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)

    body = {"complete_info": [{"courier_id": 1, "order_id": 1, "complete_time": complete_time}]}
    response = client.post("/orders/complete", json=body)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_valid_complete_one_order(client):
    couriers = generate_couriers(1)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    orders = generate_valid_orders(1)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    pre_completed_time = "2023-04-28T17:10:08.554Z"
    body = {"complete_info": [{"courier_id": 1, "order_id": 1, "complete_time": pre_completed_time}]}
    response = client.post("/orders/complete", json=body)
    response_data = response.json()
    completed_date = response_data[0].pop("completed_time")
    response_data[0].pop("order_id")
    assert completed_date == pre_completed_time
    for key, value in response_data[0].items():
        assert orders[0].dict()[key] == value


@pytest.mark.asyncio()
async def test_valid_complete_ten_orders(client):
    couriers = generate_couriers(1)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    orders = generate_valid_orders(10)
    dto_orders = [api_models_to_dto(order) for order in orders]
    await OrdersService.add_orders(dto_orders)
    tested_completed_time = "2023-04-28T17:10:08.554Z"
    body = {"complete_info": []}
    for i in range(1, 11):
        body["complete_info"].append({"courier_id": 1, "order_id": i, "complete_time": tested_completed_time})
    response = client.post("/orders/complete", json=body)
    response_data = response.json()
    for i, result_order in enumerate(response_data):
        completed_date = result_order.pop("completed_time")
        result_order.pop("order_id")
        assert completed_date == tested_completed_time
        for key, value in result_order.items():
            assert orders[i].dict()[key] == value


@pytest.mark.asyncio()
@pytest.mark.parametrize("working_hours", [[1, 2], [0, 0], ["10-00-13-00"], ["st:r-s:tr"], ["str-str"]])
async def test_post_couriers_with_invalid_working_hours(client, working_hours):
    json_orders = {"couriers": [{"courier_type": "FOOT", "regions": [1], "working_hours": working_hours}]}
    response = client.post("/couriers", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_type", ["fot", "word", 1, -1, 0.9, "FOOD"])
async def test_post_couriers_with_invalid_courier_type(client, courier_type):
    json_orders = {"couriers": [{"courier_type": courier_type, "regions": [1], "working_hours": ["10:00-13:00"]}]}
    response = client.post("/couriers", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("regions", [1, ["a", "b", "c"], -1, [-10, 9.2, 19]])
async def test_post_couriers_with_invalid_regions(regions, client):
    json_orders = {"couriers": [{"courier_type": "AUTO", "regions": regions, "working_hours": ["10:00-13:00"]}]}
    response = client.post("/couriers", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("courier_type", "regions"), [("FOOT", [1, 2]), ("FOOT", [1, 2, 3]), ("BIKE", [1, 2, 3]), ("AUTO", [1, 2, 3, 4])]
)
async def test_post_couriers_with_dismatch_type_regions(client, courier_type, regions):
    json_orders = {"couriers": [{"courier_type": courier_type, "regions": regions, "working_hours": ["10:00-13:00"]}]}
    response = client.post("/couriers", json=json_orders)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_post_valid_courier_status(client):
    json_orders = {"couriers": [{"courier_type": "AUTO", "regions": [1, 2, 3], "working_hours": ["10:00-13:00"]}]}
    response = client.post("/couriers", json=json_orders)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
async def test_post_valid_courier_create_couriers(client, get_session):
    json_orders = {"couriers": [{"courier_type": "AUTO", "regions": [1, 2, 3], "working_hours": ["10:00-13:00"]}]}
    response = client.post("/couriers", json=json_orders)
    response_courier = response.json()["couriers"][0]
    async with get_session() as session:
        db_couriers_query = select(Courier)
        db_couriers_cursor = await session.execute(db_couriers_query)
        db_couriers_res = db_couriers_cursor.scalars().all()
        db_added_courier = db_couriers_res[0]
        assert len(db_couriers_res) == 1
        assert db_added_courier.courier_type == response_courier["courier_type"]
        assert [area.area_number for area in db_added_courier.areas] == response_courier["regions"]
        await session.rollback()


@pytest.mark.asyncio()
async def test_10k_post_couriers(client, get_session):
    couriers = generate_couriers(10000)
    api_couriers = [x.dict() for x in couriers.couriers]
    response = client.post("/couriers", json={"couriers": api_couriers})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["couriers"]) == 10000
    async with get_session() as session:
        db_couriers_query = select(Courier)
        db_couriers_cursor = await session.execute(db_couriers_query)
        db_couriers_res = db_couriers_cursor.scalars().all()
        assert len(db_couriers_res) == 10000
        await session.rollback()


@pytest.mark.asyncio()
async def test_get_couriers_without_params(client):
    response = client.get("/couriers")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio()
@pytest.mark.parametrize("limit", [-1, 12.2, "string", 0, 12345678900000])
async def test_get_couriers_with_invalid_limit(client, limit):
    response = client.get("/couriers", params={"limit": limit})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("offset", [-1, "sadadas", -3.22, 14.5, 12345678900000])
async def test_get_couriers_with_invalid_offset(client, offset):
    response = client.get("/couriers", params={"offset": offset})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_get_coureirs_with_limit_1(client):
    couriers = generate_couriers(1)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    response = client.get("/couriers").json()
    response_courier = response["couriers"][0]
    assert response_courier["courier_type"] == couriers.couriers[0].courier_type
    assert response_courier["courier_id"] == 1
    assert couriers.couriers[0].regions == response_courier["regions"]
    assert response_courier["working_hours"] == couriers.couriers[0].working_hours


@pytest.mark.asyncio()
async def test_get_couriers_with_limit_2(client):
    couriers = generate_couriers(100)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    response = client.get("/couriers", params={"limit": 2})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["couriers"]) == 2
    response_data = response.json()
    assert response_data["couriers"][0]["courier_type"] == couriers.couriers[0].courier_type
    assert response_data["couriers"][0]["courier_id"] == 1
    assert couriers.couriers[0].regions == response_data["couriers"][0]["regions"]
    assert response_data["couriers"][0]["working_hours"] == couriers.couriers[0].working_hours

    assert response_data["couriers"][1]["courier_type"] == couriers.couriers[1].courier_type
    assert response_data["couriers"][1]["courier_id"] == 2
    assert couriers.couriers[1].regions == response_data["couriers"][1]["regions"]
    assert response_data["couriers"][1]["working_hours"] == couriers.couriers[1].working_hours


@pytest.mark.asyncio()
async def test_get_couriers_with_limit_2_offset_1(client):
    couriers = generate_couriers(100)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    response = client.get("/couriers", params={"offset": 1})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["couriers"]) == 1
    response_data = response.json()
    assert response_data["couriers"][0]["courier_type"] == couriers.couriers[1].courier_type
    assert response_data["couriers"][0]["courier_id"] == 2
    assert couriers.couriers[1].regions == response_data["couriers"][0]["regions"]
    assert response_data["couriers"][0]["working_hours"] == couriers.couriers[1].working_hours


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_id", [0, -1, 12.51, "not_id", 12345678900000])
async def test_get_courirer_by_invalid_id(client, courier_id):
    response = client.get(f"/couriers/{courier_id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_id", [2, 3, 4, 5, 10, 1000])
async def test_get_non_exist_courier(client, courier_id):
    response = client.get(f"/couriers/{courier_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_exist_courier(client):
    couriers = generate_couriers(100)
    dto_couriers = [api_models_to_dto(courier) for courier in couriers.couriers]
    await CourierService.add_couriers(dto_couriers)
    for courier_num in range(1, 101):
        response_courier = client.get(f"/couriers/{courier_num}").json()
        assert response_courier["courier_id"] == courier_num
        assert response_courier["courier_type"] == couriers.couriers[courier_num - 1].courier_type
        assert response_courier["regions"] == couriers.couriers[courier_num - 1].regions
        assert response_courier["working_hours"] == couriers.couriers[courier_num - 1].working_hours


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_id", [0, -1, 12.51, "not_id", 12345678900000])
async def test_get_statistic_with_invalid_courier_id(client, courier_id):
    response = client.get(f"/couriers/meta-info/{courier_id}", params={"startDate": "2023-01-20", "endDate": "2023-01-21"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("startDate", [0, "01-20-2023", "str-str-str"])
async def test_get_statistic_with_invalid_startDate(client, startDate):
    response = client.get(f"/couriers/meta-info/{1}", params={"startDate": startDate, "endDate": "2023-01-21"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("endDate", [[1, 2], [0, 0], ["01-20-2023"], ["str-str-str"]])
async def test_get_statistic_with_invalid_endDate(client, endDate):
    response = client.get(f"/couriers/meta-info/{1}", params={"startDate": "2023-01-21", "endDate": endDate})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize("courier_id", [2, 3, 4, 5, 10, 1000])
async def test_get_statistic_with_non_exist_courier(client, courier_id):
    response = client.get(f"/couriers/meta-info/{courier_id}", params={"startDate": "2023-01-20", "endDate": "2023-01-21"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_get_statistic_with_delta_0_days(client):
    response = client.get(f"/couriers/meta-info/{1}", params={"startDate": "2023-01-21", "endDate": "2023-01-21"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
async def test_get_statistic_with_negative_timedelta(client):
    response = client.get(f"/couriers/meta-info/{1}", params={"startDate": "2023-01-21", "endDate": "2023-01-19"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio()
@pytest.mark.parametrize(("courier_type", "coeff"), [("FOOT", 3), ("BIKE", 2), ("AUTO", 1)])
async def test_get_valid_statistic(client, courier_type, coeff):
    api_couriers = [
        {"courier_type": courier_type, "regions": [1], "working_hours": ["10:00-14:30"]},
    ]
    courier_response = client.post("/couriers", json={"couriers": api_couriers})
    assert courier_response.status_code == status.HTTP_200_OK
    orders = generate_valid_orders(24)
    api_orders = [x.dict() for x in orders]
    orders_response = client.post("/orders", json={"orders": api_orders})
    assert orders_response.status_code == status.HTTP_200_OK
    tested_completed_time = "2023-04-28T17:10:08.554Z"
    body = {"complete_info": []}
    earn_coeff = {"FOOT": 2, "BIKE": 3, "AUTO": 4}
    total_cost = sum([order.cost for order in orders]) * earn_coeff[courier_type]
    for i in range(1, 25):
        body["complete_info"].append({"courier_id": 1, "order_id": i, "complete_time": tested_completed_time})
    client.post("/orders/complete", json=body)
    response = client.get(f"/couriers/meta-info/{1}", params={"startDate": "2023-04-28", "endDate": "2023-04-29"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert total_cost == response_data["earnings"]
    assert coeff == response_data["rating"]
    assert courier_type == response_data["courier_type"]
    assert api_couriers[0]["regions"] == response_data["regions"]
    assert api_couriers[0]["working_hours"] == response_data["working_hours"]
