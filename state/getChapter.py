from config import dp, bot
from aiogram import types
from handlers.check_callback_query import subscribe
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)
from utils.API import getVolumes
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger


class check(StatesGroup):
    getChapter = State()  # check:getChapter


giveMeChaptersData = CallbackData('Act', 'id', 'numVolume', 'action')


@dp.callback_query_handler(subscribe.filter(action=['giveMeVolumes']))
async def giveMeVolumes(callback_query: types.CallbackQuery, callback_data: CallbackData):
    giveMeChapterBTN = InlineKeyboardMarkup(row_width=2)
    data = await getVolumes(callback_data["id"])
    i = 0
    for item in data:
        giveMeChapterBTN.insert(InlineKeyboardButton(str(item["name"]),
                                                     callback_data=giveMeChaptersData.new(action='giveMeChapters',
                                                                                          id=callback_data["id"],
                                                                                          numVolume=i)))
        i += 1

    await bot.send_message(callback_query.message.chat.id, "Выберите том:", reply_markup=giveMeChapterBTN)


@dp.callback_query_handler(giveMeChaptersData.filter(action=['giveMeChapters']))
async def giveMeChapters(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await getVolumes(callback_data["id"])
    await bot.edit_message_text(
        f'Выберите главу по номеру: \n1-{len(data[int(callback_data["numVolume"])]["chapters"]) - 1}',
        callback_query.message.chat.id, callback_query.message.message_id)
    await check.getChapter.set()
    data[0]["numVolume"] = int(callback_data["numVolume"])
    await state.set_data(data=data)


@dp.message_handler(state=check.getChapter)
async def giveMeChapter(message: types.Message, state: FSMContext):
    data = await state.get_data()
    Link = InlineKeyboardMarkup()
    try:
        Link.add(InlineKeyboardButton('Ссылка на главу',
                                      url=data[int(data[0]["numVolume"])]["chapters"][int(message.text) - 1]["url"]))
        await bot.send_message(message.chat.id, data[int(data[0]["numVolume"])]["chapters"][int(message.text) - 1]["name"],
                               reply_markup=Link)
        await state.finish()
    except:
        pass
    logger.info(f'{message.from_user.full_name}: Ссылка на главу')
