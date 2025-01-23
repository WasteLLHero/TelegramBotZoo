
import asyncio
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message

async def simulate_typing(message: Message, typing_interval: float = 4.0):
    """Функция эмулирует действие 'typing' для бота в чате.

    Бот будет показывать действие 'typing' через заданные интервалы времени.

    Аргументы:
        message (types.Message): Объект сообщения из aiogram.
        typing_interval (float): Интервал времени в секундах между действиями 'typing'.
    """
    while True:
        try:
            await message.bot.send_chat_action(message.chat.id, 'typing')
            await asyncio.sleep(typing_interval)
        except TelegramRetryAfter as e:
            # Telegram попросил повторить попытку через e.retry_after секунд
            await asyncio.sleep(e.retry_after)
        except Exception as e:
            # Логирует и обрабатывает другие исключения
            print(f"Произошла ошибка: {e}")
            break # Возможно, стоит выйти из цикла или сделать что-то другое