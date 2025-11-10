"""Авторизация для API endpoints."""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY_VALUE = "dotainstructor"


async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """
    Проверка API ключа.
    
    Args:
        api_key: API ключ из заголовка X-API-Key
    
    Returns:
        str: API ключ, если валиден
    
    Raises:
        HTTPException: Если API ключ неверный или отсутствует
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API ключ отсутствует. Укажите заголовок X-API-Key"
        )
    
    if api_key != API_KEY_VALUE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API ключ"
        )
    
    return api_key

