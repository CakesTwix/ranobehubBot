from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from sqlalchemy import (Column, ForeignKey, Integer, String,
                        create_engine, select, UniqueConstraint, delete)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import asyncio
from loguru import logger as logging
from utils.API import getLast, getVolumes
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup)

token = ''
storage = MemoryStorage()
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)

Base = declarative_base()


class Subscribers(Base):
    __tablename__ = "subscribers"
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer)
    book_name = Column(String)
    last_chapter = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    user = relationship("User", backref='user')
    __table_args__ = UniqueConstraint('book_id', 'user_id', name='book_id_check'),


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True)


engine = create_engine(
    "sqlite:///db.sqlite",
)
Base.metadata.create_all(engine)


async def periodic():
    connection = engine.connect()
    data = await getLast()
    lastId = data[0]["id"]
    while True:
        try:
            data = await getLast()
        except Exception as err:
            logging.error(f"Невозможность проверить новые главы: {err}")
        if not data[0]["id"] == lastId:
            logging.info("Разные айдишники!")
            lastId = data[0]["id"]
            LastChapter = await getVolumes(data[0]["id"])
            for id in connection.execute(select(Subscribers).where(Subscribers.book_id == lastId).where(Subscribers.last_chapter != LastChapter[-1]["chapters"][-1]["id"])):
                try:
                    Link = InlineKeyboardMarkup()
                    Link.add(InlineKeyboardButton('Ссылка на главу', url=LastChapter[-1]["chapters"][-1]["url"]))
                    await bot.send_message(id.user_id, f'Новая глава {LastChapter[-1]["chapters"][-1]["name"]}', reply_markup=Link)
                except Exception as err:
                    engine.connect().execute(delete(User).where(User.user_id == id.user_id))
                    logging.warning(f'Питух {str(id.user_id)} - {err}')
        await asyncio.sleep(120)


async def initBot(dispatcher: Dispatcher):
    await bot.set_my_commands([
        BotCommand("last", "Новые главы"),
        BotCommand("popular", "Популярное ранобэ"),
        BotCommand("search", "<*> Поиск ранобэ"),
        BotCommand("favorites", "Избранное"),
    ])
    logging.info('Бот включен')
    asyncio.create_task(periodic())
