from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader

from app.config import API_TOKEN

security = APIKeyHeader(name='Authorization')


def check_token(token=Depends(security)):
    if token != API_TOKEN:
        raise HTTPException(status_code=400, detail='Invalid credentials')


auth = Depends(check_token)
