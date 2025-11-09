"""Обработчики для удаления программы."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import crud
from app.utils.keyboards import (
    get_main_keyboard, 
    get_programs_keyboard, 
    get_confirm_keyboard,
    get_programs_menu_keyboard
)
from app.utils.messages import format_program_list

router = Router()


@router.message(F.text == "Удалить программу")
async def start_delete_program(message: Message, session: AsyncSession):
    """Начало процесса удаления программы."""
    username = message.from_user.username
    user = await crud.get_or_create_user(session, message.from_user.id, username=username)
    programs = await crud.get_user_sessions(session, user.id)
    
    if not programs:
        await message.answer(
            "❌ У вас нет программ для удаления.",
            reply_markup=get_programs_menu_keyboard()
        )
        return
    
    text = "Выберите программу для удаления:"
    await message.answer(
        text,
        reply_markup=get_programs_keyboard(programs, prefix="delete")
    )


@router.callback_query(F.data.startswith("delete_program_"))
async def confirm_delete_program(callback: CallbackQuery, session: AsyncSession):
    """Подтверждение удаления программы."""
    session_id = int(callback.data.split("_")[-1])
    program = await crud.get_session_by_id(session, session_id)
    
    if not program:
        await callback.answer("Программа не найдена.", show_alert=True)
        return
    
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить программу «{program.name}»?\n\n"
        f"Все связанные данные будут удалены безвозвратно.",
        reply_markup=get_confirm_keyboard("delete", session_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_"))
async def process_delete_program(callback: CallbackQuery, session: AsyncSession):
    """Обработка подтверждения удаления."""
    session_id = int(callback.data.split("_")[-1])
    program = await crud.get_session_by_id(session, session_id)
    
    if not program:
        await callback.answer("Программа не найдена.", show_alert=True)
        return
    
    program_name = program.name
    success = await crud.delete_session(session, session_id)
    
    if success:
        await callback.message.edit_text(
            f"✅ Программа «{program_name}» успешно удалена."
        )
        await callback.answer("Программа удалена")
    else:
        await callback.message.edit_text("❌ Ошибка при удалении программы.")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete_program(callback: CallbackQuery):
    """Отмена удаления программы."""
    await callback.message.edit_text("Удаление отменено.")
    await callback.answer()

