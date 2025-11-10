"""API routes для получения данных о пользователях и программах."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.auth import verify_api_key
from app.db.init_db import async_session_maker
from app.db.models import User, Session
from app.db import crud

router = APIRouter()


async def get_db_session():
    """Dependency для получения сессии базы данных."""
    async with async_session_maker() as session:
        yield session


@router.get("/users", dependencies=[Depends(verify_api_key)])
async def get_users_with_programs(session: AsyncSession = Depends(get_db_session)):
    """
    Получить список всех пользователей с их программами и количеством программ.
    
    Требует авторизации через API ключ в заголовке X-API-Key.
    
    Returns:
        dict: Словарь с ключом "users", содержащий список пользователей
    """
    try:
        # Получаем всех пользователей
        result = await session.execute(
            select(User).order_by(User.created_at)
        )
        users = result.scalars().all()
        
        # Для каждого пользователя получаем программы и считаем их количество
        users_data = []
        for user in users:
            # Получаем все программы пользователя
            programs = await crud.get_user_sessions(session, user.id)
            programs_count = len(programs)
            
            # Формируем данные о программах
            programs_data = []
            for program in programs:
                programs_data.append({
                    "id": program.session_id,
                    "name": program.name,
                    "created_at": program.created_at.isoformat() if program.created_at else None
                })
            
            users_data.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "programs_count": programs_count,
                "programs": programs_data
            })
        
        return {
            "users": users_data,
            "total_users": len(users_data),
            "total_programs": sum(u["programs_count"] for u in users_data)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении данных: {str(e)}"
        )

