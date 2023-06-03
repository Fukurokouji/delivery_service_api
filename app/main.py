from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette import status

from app.api.routes.main_routes import router as all_routes
from app.utils.rps_limiter import limiter


def custom_request_validation_error(request: Request, exc: Exception) -> JSONResponse:
    """function for send jsonresponse on RequestValidationError with 400 HTTP status"""
    return JSONResponse({"message": "error"}, status_code=status.HTTP_400_BAD_REQUEST)


app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(all_routes)
app.add_exception_handler(RequestValidationError, custom_request_validation_error)
