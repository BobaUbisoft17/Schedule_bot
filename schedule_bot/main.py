import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.dispatcher.filters import Text as TextFilter

from file_service import get_schedule
import keyboard as kb


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


# TODO: add handler filter
@dp.message_handler()
async def send_schedule(message: Message):
	await message.answer(
		get_schedule(message.text),
		reply_markup=kb.markup,
		)
