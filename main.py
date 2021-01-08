from aiogram import executor
import asyncio
from config import initBot, dp
from handlers import check_callback_query, favorites, last, popular, search, send, start, subscribe_callback_query


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=initBot)
