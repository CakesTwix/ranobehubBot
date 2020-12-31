import aiohttp
from aiogram import types
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData
from loguru import logger as logging

from config import dp

subscribe = CallbackData('Act', 'id', 'action')


@dp.message_handler(commands=["search"])
@dp.throttled(rate=1)
async def search_command(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://ranobehub.org/api/fulltext/ranobe?query=' + message.get_args()) as get:
                answer = await get.json()
                await session.close()

        ListUpdates = InlineKeyboardMarkup(row_width=5)
        if not answer["data"] == []:
            titles = 'Результат поиска: \n\n'
        else:
            titles = 'Ничего не найдено :( \n\n'

        i = 1
        for item in answer["data"]:
            ListUpdates.insert(InlineKeyboardButton(str(i), callback_data=subscribe.new(action='check', id=item["id"])))
            titles += f'[{i}] - ' + item["names"]["rus"] + '\n'
            i += 1
        await message.answer(titles, reply_markup=ListUpdates)
    except:
        pass
    logging.info(str(message.from_user.username) + ' | ' + message.text)
