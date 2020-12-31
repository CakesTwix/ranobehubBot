import typing

from aiogram import types
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData
from loguru import logger as logging
from sqlalchemy import delete, insert

from config import Subscribers, bot, dp, engine
from utils.API import searchID, getVolumes

subscribe = CallbackData('Act', 'id', 'action')


@dp.callback_query_handler(subscribe.filter(action=['subscribe']))
async def subscribe_callback_query(callback_query: types.CallbackQuery, callback_data: typing.Dict[int, str]):
    connection = engine.connect()
    data = await searchID(callback_data["id"])
    LastChapter = await getVolumes(callback_data["id"])
    try:
        await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Отписаться', callback_data=subscribe.new(action='unsubscribe', id=int(callback_data["id"])))).add(InlineKeyboardButton('Ссылка на ранобэ', data["url"])).add(InlineKeyboardButton('Выбрать главу', callback_data='giveMeChapter')) )

        connection.execute(insert(Subscribers).values(user_id=callback_query.from_user.id, book_id=callback_data["id"], book_name=data["names"]["rus"], last_chapter=LastChapter[-1]["chapters"][-1]["id"]))
        logging.info(str(callback_query.from_user.username) + ' | Подписался на ранобэ')
    except Exception:
        pass
    finally:
        await callback_query.answer()


@dp.callback_query_handler(subscribe.filter(action=['unsubscribe']))
async def unsubscribe_callback_query(callback_query: types.CallbackQuery, callback_data: typing.Dict[int, str]):
    data = await searchID( int(callback_data["id"]) )
    try:
        await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Подписаться', callback_data=subscribe.new(action='subscribe', id=int(callback_data["id"]) ))).add(InlineKeyboardButton('Ссылка на ранобэ', data["url"])).add(InlineKeyboardButton('Выбрать главу', callback_data='giveMeChapter')) )
        logging.info(str(callback_query.from_user.username) + ' | Отписался от ранобэ')
        engine.connect().execute(delete(Subscribers).where(Subscribers.user_id == callback_query.from_user.id).where(Subscribers.book_id == callback_data["id"])).first()
    except Exception :
        pass
        # logging.error(str(callback_query.from_user.username) + ' | ' + str(err))
    finally:
        await callback_query.answer()
