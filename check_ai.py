"""Скрипт для проверки настройки AI."""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 ПРОВЕРКА НАСТРОЙКИ AI")
print("=" * 60)
print()

# Проверяем провайдера
ai_provider = os.getenv("AI_PROVIDER", "none")
print(f"AI_PROVIDER: {ai_provider}")

if ai_provider == "none":
    print("❌ AI отключен (AI_PROVIDER=none)")
    print()
    print("Для включения AI установите переменную окружения:")
    print("  AI_PROVIDER=openai  # или yandex, anthropic, google, groq, ollama")
    print()
    print("И установите соответствующий API ключ:")
    print("  • OpenAI: OPENAI_API_KEY")
    print("  • Yandex: YANDEX_API_KEY и YANDEX_FOLDER_ID")
    print("  • Anthropic: ANTHROPIC_API_KEY")
    print("  • Google: GOOGLE_API_KEY")
    print("  • Groq: GROQ_API_KEY")
    print("  • Ollama: OLLAMA_URL (по умолчанию http://localhost:11434)")
else:
    print(f"✅ AI провайдер: {ai_provider}")
    print()
    
    # Проверяем ключи для каждого провайдера
    if ai_provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key:
            print(f"✅ OPENAI_API_KEY: установлен ({key[:10]}...)")
        else:
            print("❌ OPENAI_API_KEY: не установлен")
    
    elif ai_provider == "yandex":
        api_key = os.getenv("YANDEX_API_KEY")
        folder_id = os.getenv("YANDEX_FOLDER_ID")
        if api_key:
            print(f"✅ YANDEX_API_KEY: установлен ({api_key[:10]}...)")
        else:
            print("❌ YANDEX_API_KEY: не установлен")
        if folder_id:
            print(f"✅ YANDEX_FOLDER_ID: установлен")
        else:
            print("❌ YANDEX_FOLDER_ID: не установлен")
    
    elif ai_provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            print(f"✅ ANTHROPIC_API_KEY: установлен ({key[:10]}...)")
        else:
            print("❌ ANTHROPIC_API_KEY: не установлен")
    
    elif ai_provider == "google":
        key = os.getenv("GOOGLE_API_KEY")
        if key:
            print(f"✅ GOOGLE_API_KEY: установлен ({key[:10]}...)")
        else:
            print("❌ GOOGLE_API_KEY: не установлен")
    
    elif ai_provider == "groq":
        key = os.getenv("GROQ_API_KEY")
        if key:
            print(f"✅ GROQ_API_KEY: установлен ({key[:10]}...)")
        else:
            print("❌ GROQ_API_KEY: не установлен")
    
    elif ai_provider == "ollama":
        url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        print(f"✅ OLLAMA_URL: {url}")
        print("   (Ollama не требует API ключа)")

print()
print("=" * 60)
print("📝 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ")
print("=" * 60)
print()
print("1. Для локальной разработки:")
print("   Создайте файл .env в корне проекта и добавьте:")
print("   AI_PROVIDER=groq")
print("   GROQ_API_KEY=your_key_here")
print()
print("2. Для Railway:")
print("   Перейдите в Settings → Variables и добавьте:")
print("   AI_PROVIDER=groq")
print("   GROQ_API_KEY=your_key_here")
print()
print("3. После добавления переменных перезапустите бота")
print("=" * 60)

