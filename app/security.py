from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader

from app.config import API_TOKEN

security = APIKeyHeader(name='Authorization')


def check_token(token=Depends(security)):
    """
    Check if the provided token matches the API token.

    Args:
        token (str): Token provided in the request header.

    Raises:
        HTTPException: If the token does not match the API token.

    Returns:
        None
    """
    if token != API_TOKEN:
        raise HTTPException(status_code=400, detail='Invalid credentials')


auth = Depends(check_token)
