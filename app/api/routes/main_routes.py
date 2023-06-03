from fastapi import APIRouter

from app.api.routes import couriers, orders
from app.api.routes.test_routes import router as test_routes

router = APIRouter()

router.include_router(test_routes)
router.include_router(orders.router, prefix="/orders")
router.include_router(couriers.router, prefix="/couriers")
