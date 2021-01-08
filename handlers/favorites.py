import aiohttp
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from config import Subscribers, dp, engine
from loguru import logger as logging
from sqlalchemy import select

subscribe = CallbackData('Act', 'id', 'action')


@dp.message_handler(commands=["favorites"])
@dp.throttled(rate=1)
async def favorites_command(message: types.Message):
    connection = engine.connect()
    favorites = ""
    i = 1
    ListFavorites = InlineKeyboardMarkup(row_width=4)
    for items in connection.execute(select(Subscribers).where(Subscribers.user_id == message.from_user.id)):
        ListFavorites.insert(InlineKeyboardButton(str(i), callback_data=subscribe.new(action='check', id=items["book_id"])))
        favorites += f"[{i}] - {items.book_name}\n"
        i += 1

    try:
        await message.answer(favorites, reply_markup=ListFavorites)
    except:
        await message.answer("На данный момент у вас ничего нету в избранном.")
    logging.info(str(message.from_user.username) + ' | ' + message.text)
