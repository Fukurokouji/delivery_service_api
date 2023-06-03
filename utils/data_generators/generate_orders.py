from random import choice, randint, uniform

from app.models.request_models import OrderRequestModel

TIMEDELTA_CHOICES = [
    "10:00-20:00",
    "09:00-09:30",
    "15:00-16:00",
    "16:25-17:00",
    "00:00-01:00",
    "01:00-02:30",
    "03:00-04:00",
    "05:25-05:45",
]


def generate_valid_orders(order_count: int) -> OrderRequestModel:
    """Функция генерации заказов для тестов"""
    orders = []
    for _ in range(order_count):
        delivery_hours_delta_count = randint(1, 8)
        delivery_hours = []
        for _ in range(delivery_hours_delta_count):
            delivery_hours.append(choice(TIMEDELTA_CHOICES))
        regions = randint(1, 99)
        weight = uniform(0.01, 10)
        cost = randint(10, 10000)
        orders.append(OrderRequestModel(weight=weight, regions=regions, delivery_hours=delivery_hours, cost=cost))
    return orders
