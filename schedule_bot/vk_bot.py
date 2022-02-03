from vkbottle.dispatch.views.abc import message
from vkbottle.tools.dev import keyboard
from config import VKBOTTOKEN
from vkbottle.bot import Bot, Message
from vkbottle import PhotoMessageUploader, BaseStateGroup
import logging
from keyboard import (
    kb_get_schedule,
    kb_choice_parallel,
    kb_unsubscribe_from_mailing_list,
    kb_subscribe_to_newsletter,
    kb_memory_class,
    kb_change_class,
    kb_settings,
    parallel,
    CLASSES_NAMES,
    give_parallel,
)
from db_memory_class import add_class_and_id, check_class_id, del_class_id, get_class_id
from vkbottle.dispatch.rules.base import ChatActionRule, StateRule
from vkbottle_types.events import GroupJoin
from file_service import get_schedule_class
from database_users import add_id, check_id, del_id, create_database
from db_memory_class import create_db
from schedule_parser import parse
import asyncio


class States_memory_class(BaseStateGroup):
    class_name = 0


class States_change_class(BaseStateGroup):
    class_name = 0


bot = Bot(token=VKBOTTOKEN)
bot.loop_wrapper.add_task(parse(bot))
logging.basicConfig(level=logging.INFO)


@bot.on.private_message(text="Начать")
async def hi_handler(message: Message):
    """Функция для ответа на сообщение 'Начать'.

    Фильтрует сообщения и отвечает только на 'Начать',
    возвращает текстовое сообщение и клавиатуру."""
    await add_class_and_id(message.peer_id)
    users_info = await bot.api.users.get(message.from_id)
    await message.answer(
        message="Здравствуйте, {}".format(users_info[0].first_name),
        keyboard=kb_get_schedule,
    )


@bot.on.private_message(
    text="Настроить уведомления", payload={"cmd": "set_notifications"}
)
async def customize_notifications(message: Message):
    """Функция для ответа на сообщение 'Настроить уведомления'.

    Фильтрует сообщения и отвечает только на 'Настроить уведомления',
    если пользователя нет в базе данных, то возвращает текстовое сообщение и
    клавиатуру с кнопкой 'Подписаться на рассылку',
    иначе возвращает текстовое сообщение и клавиатуру с кнопкой 'Отписаться от рассылки'"""
    if await check_id(message.peer_id):
        await message.answer(
            "Отписаться от рассылки?",
            keyboard=kb_unsubscribe_from_mailing_list,
        )
    else:
        await message.answer(
            "Подписаться на рассылку?",
            keyboard=kb_subscribe_to_newsletter,
        )


@bot.on.private_message(
    text="Подписаться на рассылку", payload={"cmd": "subscribe_on_newsletter"}
)
async def subscribe_newsletter(message: Message):
    """Функция для ответа на сообщение 'Подписаться на рассылку'.

    Фильтрует сообщения и отвечает только на 'Подписаться на рассылку',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с кнопкой 'Отписаться от рассылки'"""
    if await check_id(message.peer_id):
        await message.answer(
            "Вы уже подписаны", keyboard=kb_unsubscribe_from_mailing_list
        )
    else:
        await add_id(message.peer_id)
        await message.answer(
            "Вы успешно подписались на уведомления, мы сообщим, если появится новое расписание",
            keyboard=kb_unsubscribe_from_mailing_list,
        )


@bot.on.private_message(
    text="Отписаться от рассылки", payload={"cmd": "unsubscribe_on_newsletter"}
)
async def unsubscribe_from_mailing_list(message: Message):
    """Функция для ответа на сообщение 'Отписаться от рассылки'.

    Фильтрует сообщения и отвечает только на 'Отписаться от рассылки',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с кнопкой 'Подписаться на рассылку'"""
    user_info = await bot.api.users.get(message.from_id)
    if await check_id(message.peer_id):
        await del_id(message.peer_id)
        await message.answer(
            "Вы успешно отписались от рассылки",
            keyboard=kb_subscribe_to_newsletter,
        )
    else:
        await message.answer(
            "Вы не подписаны на рассылку",
            keyboard=kb_subscribe_to_newsletter,
        )


@bot.on.private_message(text="Узнать расписание", payload={"cmd": "get_schedule"})
async def choice_parallel(message: Message):
    """Функция для ответа на сообщение 'Узнать расписание'.

    Фильтрует сообщения и отвечает только на 'Узнать расписание',
    добавляет id пользователя в базу данных для оповещения о появлении нового расписания,
    возвращает текстовое сообщение и клавиатуру для выбора параллели."""
    if await check_class_id(message.peer_id):
        class_name = await get_class_id(message.peer_id)
        file_path = await get_schedule_class(class_name)
        photo = [
            await PhotoMessageUploader(bot.api).upload(file)
            for file in sorted(file_path)
        ]
        await message.answer(
            f"Расписание {class_name}", attachment=photo, keyboard=kb_get_schedule
        )
    else:
        await message.answer("Выберите вашу параллель", keyboard=kb_choice_parallel)


@bot.on.private_message(text="Настройки", payload={"cmd": "settings"})
async def change_settings(message: Message):
    await message.answer("Переходим...", keyboard=kb_settings)


@bot.on.private_message(text="Запоминание класса", payload={"cmd": "set_memory_class"})
async def memory_class(message: Message):
    if not await check_class_id(message.peer_id):
        await message.answer("Переходим...", keyboard=kb_memory_class)
    else:
        await message.answer("Переходим...", keyboard=kb_change_class)


@bot.on.private_message(text=parallel, payload={"cmd": "parallel"})
async def choice_class(message: Message):
    """Функция для ответа на сообщение, в котором указаны параллели от 5-х до 11-х классов.

    Фильтрует сообщения и отвечает только на парралель,
    генерирует клавиатуру взависимости от выбранной параллели,
    возвращает текстовое сообщение и клавиатуру для выбора класса."""
    await message.answer(
        "Выберите ваш класс",
        keyboard=await give_parallel(message.text.split()[0]),
    )


@bot.on.private_message(
    text="Удалить данные о моём классе", payload={"cmd": "del_my_class"}
)
async def del_class(message: Message):
    if await check_class_id(message.peer_id):
        await del_class_id(message.peer_id)
        await message.answer(
            "Все данные о вашем классе были удалены", keyboard=kb_settings
        )
    else:
        await message.answer("Не ломайте бота, пожалуйста", kb_settings)


@bot.on.private_message(text="Назад", payload={"cmd": "back1"})
async def back(message: Message):
    await message.answer("Возвращаемся...", keyboard=kb_settings)


@bot.on.private_message(text="Назад", payload={"cmd": "back2"})
async def back(message: Message):
    await message.answer("Возвращаемся...", keyboard=kb_get_schedule)


@bot.on.private_message(text=CLASSES_NAMES, payload={"cmd": "class_"})
async def get_schedule(message: Message):
    """Функция для отправки фотографий с расписанием.

    Функция фильтрует сообщения и отвечает тольок на те, в которых указан класс из списка CLASSES_NAMES,
    возвращает изображение или изображения(взависимости от класса и дня недели) + текст."""
    file_path = await get_schedule_class(message.text)
    photo = [
        await PhotoMessageUploader(bot.api).upload(file) for file in sorted(file_path)
    ]
    await message.answer(
        f"Расписание {message.text}", attachment=photo, keyboard=kb_get_schedule
    )


@bot.on.private_message(lev="Запомнить мой класс", payload={"cmd": "memory_my_class"})
async def class_memory(message: Message):
    if not await check_class_id(message.peer_id):
        await bot.state_dispenser.set(message.peer_id, States_memory_class.class_name)
        return "Введите номер вашего класса и букву в верхнем регистре без пробелов"
    else:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Не ломайте бота, пожалуйста", keyboard=kb_settings)


@bot.on.private_message(state=States_memory_class.class_name)
async def get_class_name(message: Message):
    if message.text in CLASSES_NAMES:
        await add_class_and_id(message.peer_id, message.text)
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer(
            "Мы вас запомнили, теперь вам не нужно выбирать класс и параллель",
            keyboard=kb_settings,
        )
    else:
        await bot.state_dispenser.set(message.peer_id, States_memory_class.class_name)
        return "Вы ввели некорректные данные, попробуйте ещё раз"


@bot.on.chat_message(ChatActionRule("chat_invite_user"))
async def hi_handler(message: Message):
    await message.answer("Здравствуйте, я Джарвиз, рад работать в вашей беседе")


@bot.on.private_message(lev="Изменить класс", payload={"cmd": "change_my_class"})
async def change_class(message: Message):
    if await check_class_id(message.peer_id):
        await bot.state_dispenser.set(message.peer_id, States_change_class.class_name)
        return "Введите номер вашего класса и букву в верхнем регистре без пробелов"


@bot.on.private_message(state=States_change_class.class_name)
async def select_class(message: Message):
    if message.text in CLASSES_NAMES:
        await add_class_and_id(message.peer_id, message.text)
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Вы успешно изменили класс", keyboard=kb_settings)
    else:
        await bot.state_dispenser.set(message.peer_id, States_change_class.class_name)
        return "Вы ввели некорректные данные, попробуйте ещё раз"


@bot.on.private_message(text="Помощь", payload={"cmd": "help"})
async def get_help(message: Message):
    await message.answer(BOT_SUPPORT)


@bot.on.private_message()
async def other(message: Message):
    """Функция для обработки сообщений, на которые не настроены фильтры"""
    await message.answer("Я вас не понимаю", keyboard=kb_get_schedule)


def main():
    """Функция, отвечающая за запуск бота.

    Функция запускает код бота, а вызывает функцию для запуска парсера,
    создвёт доп. процесс."""
    create_db()
    create_database()
    bot.run_forever()
