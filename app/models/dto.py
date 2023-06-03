from dataclasses import dataclass


@dataclass
class OrderDto:
    """Dto model for order"""

    weight: float
    regions: int
    delivery_hours: list[str]
    cost: int


@dataclass
class CourierDto:
    """Dto model for courier"""

    courier_type: str
    regions: list[int]
    working_hours: list[str]


@dataclass
class CompleteOrderDto:
    """Dto model for complete order"""

    courier_id: int
    order_id: int
    complete_time: str
