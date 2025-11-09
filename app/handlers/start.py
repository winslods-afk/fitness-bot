"""Обработчики команды /start и главного меню."""
from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.db import crud
from app.utils.keyboards import get_main_keyboard, get_programs_menu_keyboard
from app.utils.messages import get_welcome_message
from app.config import DB_PATH

router = Router()

# ID администраторов (замените на свой Telegram ID)
ADMIN_IDS = []  # Добавьте сюда ваш Telegram ID, например: [123456789]

# Username администраторов (без @)
ADMIN_USERNAMES = ["dota_instructor"]  # Добавьте сюда username администраторов


@router.message(F.text == "Перезапустить Бота")
async def cmd_restart(message: Message, state: FSMContext):
    """Обработчик кнопки перезапуска."""
    await state.clear()
    await message.answer(
        get_welcome_message(),
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "Мои Программы тренировок")
async def show_programs_menu(message: Message, state: FSMContext):
    """Показать подменю 'Мои Программы тренировок'."""
    await message.answer(
        "📋 <b>Мои Программы тренировок</b>\n\n"
        "Выберите действие:",
        reply_markup=get_programs_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(F.text == "◀️ Назад")
async def back_to_main_menu(message: Message, state: FSMContext):
    """Возврат в главное меню."""
    await state.clear()
    await message.answer(
        "Главное меню",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "/start")
@router.message(F.text == "/restart")
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """Обработчик команды /start."""
    await state.clear()
    
    # Создаём или получаем пользователя
    user = await crud.get_or_create_user(session, message.from_user.id)
    
    await message.answer(
        get_welcome_message(),
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "/help")
async def cmd_help(message: Message):
    """Обработчик команды /help."""
    help_text = (
        "📖 Помощь по использованию бота:\n\n"
        "• /start — начать работу с ботом\n"
        "• /restart — перезапустить бота\n"
        "• /myprograms — показать все ваши программы\n\n"
        "Основные функции:\n"
        "• Добавить программу — создать новую программу тренировок\n"
        "• Удалить программу — удалить существующую программу\n"
        "• Начать тренировку — провести тренировку по сохранённой программе\n\n"
        "При добавлении программы вы можете вводить упражнения в разных форматах:\n"
        "• Гакк-присед — 20-16-14-12\n"
        "• Гакк-присед — 4х10\n"
        "• Гакк-присед — 4 подхода по 10 раз"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())


@router.message(F.text == "/myprograms")
async def cmd_myprograms(message: Message, session: AsyncSession):
    """Обработчик команды /myprograms."""
    user = await crud.get_or_create_user(session, message.from_user.id)
    programs = await crud.get_user_sessions(session, user.id)
    
    if not programs:
        await message.answer(
            "У вас пока нет программ. Добавьте программу через меню.",
            reply_markup=get_main_keyboard()
        )
        return
    
    from app.utils.messages import format_program_list
    text = format_program_list(programs)
    
    await message.answer(text, reply_markup=get_main_keyboard())


@router.message(F.text == "/export_db")
async def cmd_export_db(message: Message):
    """Экспорт базы данных (только для администраторов)."""
    # Проверяем права: по ID или по username
    is_admin = False
    user_id = message.from_user.id
    username = message.from_user.username or ""
    
    # Проверка по ID
    if ADMIN_IDS and user_id in ADMIN_IDS:
        is_admin = True
    
    # Проверка по username (без учета регистра)
    if not is_admin and ADMIN_USERNAMES:
        user_lower = username.lower()
        for admin_username in ADMIN_USERNAMES:
            if admin_username.lower() == user_lower:
                is_admin = True
                break
    
    if not is_admin:
        # Логируем для отладки
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            f"Access denied for /export_db. User ID: {user_id}, Username: {username}, "
            f"Admin IDs: {ADMIN_IDS}, Admin Usernames: {ADMIN_USERNAMES}"
        )
        await message.answer(
            f"❌ У вас нет прав для выполнения этой команды.\n\n"
            f"Ваш ID: {user_id}\n"
            f"Ваш username: @{username if username else 'не указан'}"
        )
        return
    
    try:
        # Проверяем существование файла базы данных
        db_path = DB_PATH
        if not os.path.exists(db_path):
            await message.answer(f"❌ База данных не найдена по пути: {db_path}")
            return
        
        # Читаем базу данных
        with open(db_path, "rb") as db_file:
            db_data = db_file.read()
            await message.answer_document(
                document=BufferedInputFile(
                    db_data,
                    filename="fitness_bot.db"
                ),
                caption="📊 База данных проекта"
            )
    except Exception as e:
        await message.answer(f"❌ Ошибка при экспорте базы данных: {str(e)}")

