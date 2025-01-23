
import asyncio
from aiogram import F, Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram import Router
from decouple import config
from async_requests import ArequestGet, ArequestGetJson
from helpers.user_quiz import user_quiz_string_frtomatter
from keyboards.start_quiz_keyboard import start_quiz_keyboard_builder
support_router = Router()

class SupportState(StatesGroup):
    waiting_for_message = State()

@support_router.callback_query(F.data == "support")
async def cmd_support(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SupportState.waiting_for_message)
    await callback.message.answer("Пожалуйста, напишите свой запрос. Я передам его администратору.")

@support_router.message(SupportState.waiting_for_message)
async def handle_support_request(message: types.Message, state: FSMContext):
    tgid = message.from_user.id

    user_message = message.text

    admins = await ArequestGetJson(f"{config('url')}/api/zoo/telegram-admin")

    user_quizs = await ArequestGetJson(f"{config('url')}/api/zoo/quiz-results/{message.from_user.id}")
    formatted_quiz_string = await user_quiz_string_frtomatter(user_quizs)

    MAX_MESSAGE_LENGTH = 4000

    def split_message(text, max_length):
        return [text[i:i + max_length] for i in range(0, len(text), max_length)]

    message_parts = split_message(formatted_quiz_string, MAX_MESSAGE_LENGTH)

    async def send_to_admin(admin):
        for part in message_parts:
            await message.bot.send_message(
                admin['tgId'],
                f"Запрос от пользователя {tgid}:\n\n{user_message}\n\n{part}"
            )

    await asyncio.gather(*[send_to_admin(admin) for admin in admins])

    await message.answer("Ваш запрос был отправлен администратору.", reply_markup=start_quiz_keyboard_builder.as_markup())

    await state.clear()