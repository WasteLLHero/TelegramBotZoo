
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
from aiogram import F
from async_requests import ArequestPost
from decouple import config
import logging
from keyboards.start_quiz_keyboard import start_quiz_keyboard_builder
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

start_router = Router()


'''Обработчик начала работы с ботом 
   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓'''

@start_router.message(
        CommandStart(), 
        F.chat.type.in_({
        "private" }
    )
)
async def start_message(message: Message):
    user_data = {
        "tgId": message.from_user.id,
        "userName": f"@{message.from_user.username}",
        "name": message.from_user.first_name,
        "secondName": message.from_user.last_name,
        "email": "",
        "phoneNumber": ""
    }
    response = await ArequestPost(f"{config("url")}/api/zoo/telegram-user/create", user_data)
    logger.info(f"{response}")
    await message.answer("Добро пожаловать, вы попали на телеграм-бота Московского зоопарка🦁. Здесь вы можете пройти ❓️викторину и определить, какое животное подходит вам больше всего и как взять его из приюта. Для того, чтобы начать викторину напишите - /quiz или нажмите на кнопку ниже", reply_markup=start_quiz_keyboard_builder.as_markup())


