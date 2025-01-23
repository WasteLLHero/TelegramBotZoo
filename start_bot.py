from bot_initialization import bot, dp, setup_bot_commands
from routers.start_router import start_router
from routers.start_quiz_router import start_quiz_router
from routers.support_router import support_router
from aiogram.types import Message
from aiogram import F
import asyncio
import os



async def main():   
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, on_startup=setup_bot_commands)

if __name__ == "__main__":
    dp.include_router(start_router)
    dp.include_router(start_quiz_router)
    dp.include_router(support_router)

    asyncio.run(main())