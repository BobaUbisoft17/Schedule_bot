import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Text as TextFilter

from file_service import get_schedule


logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("SCHEDULEBOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=["start"])
async def send_welcome(message: Message):
    await message.answer(
        "Бот, предоставяющий расписание 14 школы г. Череповца",
        reply_markup=kb.markup,
    )


@dp.message_handler(message)
async def send_schedule():
	await message.answer(
		get_schedule(message.text),
		reply_markup=kb.markup,
		)


"""@dp.message_handler(commands=["help"], state="*")
async def send_help(message):
    await message.answer("Sorry")"""
