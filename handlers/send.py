from config import dp, engine, User, bot
from sqlalchemy import select
from loguru import logger


@dp.message_handler(commands=['send'])
async def send_command(message):
    if message.from_user.username == 'CakesTwix':
        for row in engine.connect().execute(select(User)):
            try:
                await bot.send_message(row.user_id, message.text[5:])
            except Exception as err:
                logger.info(f"{str(row.user_id) } - забанил бота у себя - {err}")