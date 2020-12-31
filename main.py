from aiogram import executor
import asyncio
from config import initBot
from handlers.check_callback_query import check_callback_query
from handlers.last import last_command
from handlers.popular import popular_command
from handlers.start import start_command
from handlers.search import search_command
from handlers.send import send_command
from handlers.subscribe_callback_query import *
from state.getChapter import giveMeVolumes, giveMeChapters


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=initBot)
