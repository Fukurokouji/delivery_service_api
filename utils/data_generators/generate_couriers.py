from random import choice, randint

from app.models.request_models import AddCouriersModel, CourierRequestModel

COURIER_CHOICES = ["AUTO", "FOOT", "BIKE"]
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

courier_regions = {
    "FOOT": [randint(1, 99) for _ in range(1)],
    "BIKE": [randint(1, 99) for _ in range(2)],
    "AUTO": [randint(1, 99) for _ in range(3)],
}


def generate_couriers(n_couriers: int) -> AddCouriersModel:
    """Простой генератор валидных курьеров для тестов"""
    couriers = []
    for _ in range(n_couriers):
        working_hours_delta_count = randint(1, 8)
        working_hours = []
        for _ in range(working_hours_delta_count):
            working_hours.append(choice(TIMEDELTA_CHOICES))
        new_courier_type = choice(COURIER_CHOICES)
        regions = courier_regions[new_courier_type]
        couriers.append(CourierRequestModel(courier_type=new_courier_type, working_hours=working_hours, regions=regions))
    return AddCouriersModel(couriers=couriers)


def generate_invalid_couriers_by_type(n_couriers: int) -> AddCouriersModel:
    """Простой генератор невалидных курьеров(не соответсвует число районов и тип курьера) для тестов"""
    couriers = []
    for _ in range(n_couriers):
        working_hours_delta_count = randint(1, 8)
        working_hours = []
        for _ in range(working_hours_delta_count):
            working_hours.append(choice(TIMEDELTA_CHOICES))
        new_courier_type = choice(COURIER_CHOICES)
        if new_courier_type == "AUTO":
            regions = [randint(1, 5) for _ in range(6)]
        elif new_courier_type == "FOOT":
            regions = [randint(1, 5) for _ in range(4)]
        else:
            regions = [randint(1, 5) for _ in range(9)]
        couriers.append(CourierRequestModel(courier_type=new_courier_type, working_hours=working_hours, regions=regions))
    return AddCouriersModel(couriers=couriers)
