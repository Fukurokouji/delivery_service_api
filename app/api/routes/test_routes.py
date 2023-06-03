from fastapi import APIRouter
from starlette import status

router = APIRouter()


@router.get("/ping", name="dev:ping", status_code=status.HTTP_200_OK)
async def ping() -> str:
    return "pong"
