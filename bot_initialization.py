from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher
from decouple import config
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=config('token'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/start", description="Начать работу"),
    ]
    await bot.set_my_commands(bot_commands)
