from aiograph import Telegraph
from config import dp, bot
from handlers.check_callback_query import subscribe
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message)
from Utils.API import getVolumes, getChapterText
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from loguru import logger

telegraph = Telegraph()


class check(StatesGroup):
    getChapter = State()  # check:getChapter


giveMeChaptersData = CallbackData('Act', 'id', 'numVolume', 'action')
telegraData = CallbackData('Act', 'url', 'action')


@dp.callback_query_handler(subscribe.filter(action=['giveMeVolumes']))
async def giveMeVolumes(callback_query: CallbackQuery, callback_data: CallbackData):
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
async def giveMeChapters(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await getVolumes(callback_data["id"])
    await bot.edit_message_text(
        f'Выберите главу по номеру: \n1-{len(data[int(callback_data["numVolume"])]["chapters"]) - 1}',
        callback_query.message.chat.id, callback_query.message.message_id)
    await check.getChapter.set()
    data[0]["numVolume"] = int(callback_data["numVolume"])
    data[0]["idRanobe"] = int(callback_data["id"])
    await state.set_data(data=data)


@dp.message_handler(state=check.getChapter)
async def giveMeChapter(message: Message, state: FSMContext):
    data = await state.get_data()
    Link = InlineKeyboardMarkup()
    if message.text.isdigit():    
        try:
            Link.add(InlineKeyboardButton('Ссылка на главу',
                                  url=data[int(data[0]["numVolume"])]["chapters"][int(message.text) - 1]["url"]))
            Link.add(InlineKeyboardButton('Отправить сюда',
                                  callback_data=telegraData.new(action='telegra', url=data[int(data[0]["numVolume"])]["chapters"][int(message.text) - 1]["url"][8:])))
            await bot.send_message(message.chat.id, data[int(data[0]["numVolume"])]["chapters"][int(message.text) - 1]["name"],
                           reply_markup=Link)
            logger.info(f'{message.from_user.full_name}: Ссылка на главу')
        except IndexError:
            await message.reply("Число ушло за рамки дозволенного.")
    else:
        await message.reply("Введите правильно номер главы.")
    

@dp.callback_query_handler(telegraData.filter(action='telegra'), state=check.getChapter)
async def telegra_callback_query(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    await telegraph.create_account('ранобэ.рф Бот')
    text = await getChapterText(callback_data["url"])

    try:
        RanobeMenu = InlineKeyboardMarkup()
        url = await telegraph.create_page(title=text["name"], content=text["text"])
        RanobeMenu.add(InlineKeyboardButton('Ссылка на главу', url.url))
        await bot.send_message(callback_query.message.chat.id, text["name"], reply_markup=RanobeMenu)
    except:
        await bot.send_message(callback_query.message.chat.id, "Простите, я не умею отправлять иллюстрации\nИли проблема в другом, отпишитесь @CakesTwix")
    await state.finish()
    logger.info(f'{callback_query.from_user.full_name}: Телегра')