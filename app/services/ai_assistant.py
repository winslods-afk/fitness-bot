"""AI ассистент для ответов на сообщения пользователей."""
import os
from typing import Optional
from app.config import BOT_TOKEN

# Поддерживаемые AI провайдеры
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai, yandex, anthropic, none

# Контекст для AI
FITNESS_BOT_CONTEXT = """Ты — помощник фитнес-бота для отслеживания тренировок и рабочих весов.

Твоя задача:
- Помогать пользователям с вопросами о тренировках, питании, восстановлении
- Давать советы по технике выполнения упражнений
- Помогать с составлением программ тренировок
- Отвечать на вопросы о работе бота

Важно:
- Отвечай кратко и по делу
- Используй эмодзи для лучшей читаемости
- Если вопрос не связан с фитнесом, вежливо перенаправь на тему тренировок
- Не давай медицинских советов, только общие рекомендации

Пользователь может задавать вопросы о:
- Технике выполнения упражнений
- Прогрессе в тренировках
- Питании и восстановлении
- Работе с ботом
"""


async def get_ai_response(user_message: str, user_context: Optional[str] = None) -> Optional[str]:
    """
    Получить ответ от AI на сообщение пользователя.
    
    Args:
        user_message: Сообщение пользователя
        user_context: Дополнительный контекст о пользователе (программы, статистика)
    
    Returns:
        Ответ от AI или None, если AI не настроен
    """
    if AI_PROVIDER == "none":
        return None
    
    context = FITNESS_BOT_CONTEXT
    if user_context:
        context += f"\n\nКонтекст пользователя:\n{user_context}"
    
    try:
        if AI_PROVIDER == "openai":
            return await _get_openai_response(user_message, context)
        elif AI_PROVIDER == "yandex":
            return await _get_yandex_response(user_message, context)
        elif AI_PROVIDER == "anthropic":
            return await _get_anthropic_response(user_message, context)
        else:
            return None
    except Exception as e:
        # Логируем ошибку, но не показываем пользователю
        import logging
        logging.error(f"AI error: {str(e)}")
        return None


async def _get_openai_response(message: str, context: str) -> Optional[str]:
    """Получить ответ от OpenAI GPT."""
    try:
        import openai
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        
        client = openai.AsyncOpenAI(api_key=api_key)
        
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except ImportError:
        return None


async def _get_yandex_response(message: str, context: str) -> Optional[str]:
    """Получить ответ от Yandex GPT."""
    try:
        import aiohttp
        
        api_key = os.getenv("YANDEX_API_KEY")
        folder_id = os.getenv("YANDEX_FOLDER_ID")
        
        if not api_key or not folder_id:
            return None
        
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": "500"
            },
            "messages": [
                {"role": "system", "text": context},
                {"role": "user", "text": message}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text")
        
        return None
    except ImportError:
        return None


async def _get_anthropic_response(message: str, context: str) -> Optional[str]:
    """Получить ответ от Anthropic Claude."""
    try:
        import anthropic
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        
        client = anthropic.AsyncAnthropic(api_key=api_key)
        
        response = await client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
            max_tokens=500,
            system=context,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return response.content[0].text
    except ImportError:
        return None


def is_ai_enabled() -> bool:
    """Проверить, включен ли AI."""
    return AI_PROVIDER != "none" and os.getenv(f"{AI_PROVIDER.upper()}_API_KEY") is not None

