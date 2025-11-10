"""FastAPI приложение для API endpoints."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router

app = FastAPI(
    title="Fitness Bot API",
    description="API для получения данных о пользователях и программах тренировок",
    version="1.0.0"
)

# Настройка CORS (разрешаем все источники для простоты)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/")
async def root():
    """Корневой endpoint."""
    return {
        "message": "Fitness Bot API",
        "version": "1.0.0",
        "endpoints": {
            "users": "/api/users",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья API."""
    return {"status": "ok"}

