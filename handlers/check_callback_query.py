import typing, asyncio

from aiogram import types
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           InputFile, ParseMode)
from aiogram.utils.callback_data import CallbackData
from config import Subscribers, bot, dp, engine
from loguru import logger as logging
from sqlalchemy import select
from utils.API import searchID

subscribe = CallbackData('Act', 'id', 'action')
getChapterData = CallbackData('Act', 'url', 'id', 'action')


@dp.callback_query_handler(subscribe.filter(action=['check']))
async def check_callback_query(callback_query: types.CallbackQuery, callback_data: typing.Dict[int, str]):
    data = await searchID(callback_data["id"])

    caption = f'{data["names"]["rus"]} \n\n'
    caption += f'Понравилось 👍: {data["rating"]} \n'

    RanobeMenu = InlineKeyboardMarkup(row_width=3)
    if engine.connect().execute(select(Subscribers).where(Subscribers.user_id == callback_query.from_user.id).where(
            Subscribers.book_id == callback_data["id"])).first() is None:
        RanobeMenu.add(InlineKeyboardButton('Подписаться', callback_data=subscribe.new(action='subscribe',
                                                                                       id=int(callback_data["id"]))))
    else:
        RanobeMenu.add(InlineKeyboardButton('Отписаться', callback_data=subscribe.new(action='unsubscribe',
                                                                                      id=int(callback_data["id"]))))

    RanobeMenu.add(InlineKeyboardButton('Ссылка на ранобэ', data["url"]))
    RanobeMenu.add(InlineKeyboardButton('Выбрать главу', callback_data=subscribe.new(action='giveMeVolumes',
                                                                                     id=int(callback_data["id"]))))

    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=InputFile.from_url(data['posters']['big']),
        caption=caption,
        reply_markup=RanobeMenu,
        parse_mode=ParseMode.MARKDOWN)
    await callback_query.answer()
    logging.info(str(callback_query.from_user.username) + ' | ' + data["names"]["rus"])
