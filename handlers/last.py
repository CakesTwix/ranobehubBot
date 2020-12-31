import aiohttp
from aiogram import types
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData
from config import dp
from loguru import logger as logging
from  utils.API import getLast

subscribe = CallbackData('Act', 'id', 'action')


@dp.message_handler(commands=["last"])
@dp.throttled(rate=1)
async def last_command(message: types.Message):
    answer = await getLast()

    ListUpdates = InlineKeyboardMarkup(row_width=4)
    titles = 'Последние главы: \n\n'
    i = 1
    for item in answer:
        ListUpdates.insert(InlineKeyboardButton(str(i), callback_data=subscribe.new(action='check', id=item["id"])))
        titles += f'[{i}] - ' + item["names"]["rus"] + '\n'
        i += 1
    await message.answer(titles, reply_markup=ListUpdates)
    logging.info(str(message.from_user.username) + ' | ' + message.text)
