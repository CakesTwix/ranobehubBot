from loguru import logger as logging
from aiogram import types
from config import dp, engine, User
from sqlalchemy import insert


@dp.message_handler(commands=["start"])
@dp.throttled(rate=1)
async def start_command(message: types.Message):
    connection = engine.connect()
    try:
        if message.chat.type == types.ChatType.PRIVATE:
            connection.execute(insert(User).values(user_id=message.from_user.id))
            logging.info("Чат " + message.chat.title + " был добавлен в БД")
    except Exception:
        pass
    await message.answer("Бот на стадии разработки. Если вы случайно нашли этого бота - ничего не трогайте, "
                         "пж(если вам дал мой хозяин - разрешаю, ток будьте нежнее, это мой первый раз~~")
    logging.info(str(message.from_user.username) + ' | ' + message.text)
