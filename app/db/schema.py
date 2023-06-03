from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import TIME, TIMESTAMP
from sqlalchemy.orm import backref, relationship

from app.db.base import Base, metadata

courier_area = Table(
    "courier_area",
    metadata,
    Column("area_id", Integer, ForeignKey("area.area_id")),
    Column("courier_id", Integer, ForeignKey("courier.courier_id")),
)


class Area(Base):
    __tablename__ = "area"

    area_id = Column("area_id", Integer, primary_key=True)
    area_number = Column("area_number", Integer, nullable=False, unique=True, index=True)

    orders = relationship("Order", backref=backref("area", lazy="subquery"), lazy="dynamic")


class Order(Base):
    __tablename__ = "order"

    order_id = Column("order_id", Integer, primary_key=True)
    weight = Column("weight", Float, nullable=False)
    region = Column("region", Integer, ForeignKey("area.area_id"), nullable=False)
    cost = Column("cost", Integer, nullable=False)
    assigned = Column("assigned", Boolean, default=False)
    completed_at = Column("completed_time", TIMESTAMP(timezone=True), nullable=True)
    courier = Column("courier", Integer, ForeignKey("courier.courier_id"), nullable=True)
    delivery_hours = relationship("OrderDeliveryHour", backref=backref("order", lazy="subquery"), lazy="subquery")


class OrderDeliveryHour(Base):
    __tablename__ = "order_delivery_hour"

    pk = Column("id", Integer, primary_key=True)
    start_time = Column("start_at", TIME, nullable=False)
    end_time = Column("end_at", TIME, nullable=False)
    order_id = Column("order_id", Integer, ForeignKey("order.order_id"), nullable=False)


class CourierType(Base):
    __tablename__ = "courier_type"

    type_id = Column("id", String, primary_key=True)
    type_rating_coefficient = Column("rating_coefficient", Integer, nullable=False)
    type_salary_coefficient = Column("salary_coefficient", Integer, nullable=False)
    type_max_area = Column("max_area", Integer, nullable=False)
    max_weight_orders = Column("max_weight_orders", Integer, nullable=False)
    max_orders_count = Column("max_orders_count", Integer, nullable=False)

    couriers = relationship("Courier", backref=backref("type", lazy="subquery"), lazy="subquery")


class Courier(Base):
    __tablename__ = "courier"

    courier_id = Column("courier_id", Integer, primary_key=True)
    courier_type = Column("courier_type", String, ForeignKey("courier_type.id"), nullable=False)

    areas = relationship("Area", secondary=courier_area, backref=backref("area_courier", lazy="dynamic"), lazy="subquery")
    worked_hours = relationship("CourierWorkTime", backref=backref("courier", lazy="subquery"), lazy="subquery")
    orders = relationship("Order", backref=backref("order_courier"), lazy="dynamic")


class CourierWorkTime(Base):
    __tablename__ = "courier_work_time"

    pk = Column("id", Integer, primary_key=True)
    start_time = Column("start_at", TIME, nullable=False)
    end_time = Column("end_at", TIME, nullable=False)
    courier_id = Column("courier_id", Integer, ForeignKey("courier.courier_id"), nullable=False)
