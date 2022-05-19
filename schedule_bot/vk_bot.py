from config import VKBOTTOKEN
from vkbottle.bot import Bot, Message
from vkbottle import PhotoMessageUploader, BaseStateGroup
import logging
from keyboard import (
    hide_keyboard,
    back1,
    back2,
    back3,
    parallels_keyboard,
    school_payloads,
    kb_select_school,
    parallel,
    classes_names,
    give_parallel,
    get_schedule_keyboard,
    settings_keyboard,
    sub_keyboard,
    unsub_keyboard,
    memory_class_keyboard,
    change_class_keyboard,
    all_classes_names
)
from db_users import create_table, add_id, check_user_subscription, subscribe_on_newsletter, unsubscribe_on_newsletter, check_school_and_class, get_school_and_class, change_user_class, check_class
from vkbottle.dispatch.rules.base import ChatActionRule, StateRule
from vkbottle_types.events import GroupJoin
from file_service import get_schedule_class
from schedule_parser import schedule_parser


class States_memory_class(BaseStateGroup):
    class_name = 0


class States_change_class(BaseStateGroup):
    class_name = 0


bot = Bot(token=VKBOTTOKEN)
bot.loop_wrapper.add_task(schedule_parser(bot))
logging.basicConfig(level=logging.INFO)


@bot.on.private_message(text="Начать")
async def hi_handler(message: Message):
    """Функция для ответа на сообщение 'Начать'.

    Фильтрует сообщения и отвечает только на 'Начать',
    возвращает текстовое сообщение и клавиатуру.
    """
    await add_id(message.peer_id)
    users_info = await bot.api.users.get(message.from_id)
    await message.answer(
        message=f"Здравствуйте, {users_info[0].first_name}",
        keyboard=kb_select_school,
    )
    await message.answer("Выберите ваше учебное заведение")


@bot.on.private_message(text=["МАОУ 'СОШ №14'", "МАОУ 'СОШ №40'"], payload=school_payloads)
async def home_space(message: Message):
    await message.answer("Переходим в главное меню", keyboard=await get_schedule_keyboard(message.payload))


@bot.on.private_message(
    text="Настроить уведомления", payload=school_payloads
)
async def customize_notifications(message: Message):
    """Функция для ответа на сообщение 'Настроить уведомления'.

    Фильтрует сообщения и отвечает только на 'Настроить уведомления',
    если пользователя нет в базе данных, то возвращает текстовое сообщение и
    клавиатуру с кнопкой 'Подписаться на рассылку',
    иначе возвращает текстовое сообщение и клавиатуру с кнопкой 'Отписаться от рассылки'"""
    if await check_user_subscription(message.peer_id):
        await message.answer(
            "Отписаться от рассылки?",
            keyboard=await unsub_keyboard(message.payload),
        )
    else:
        await message.answer(
            "Подписаться на рассылку?",
            keyboard=await sub_keyboard(message.payload),
        )


@bot.on.private_message(
    text="Подписаться на рассылку", payload=school_payloads
)
async def subscribe_newsletter(message: Message):
    """Функция для ответа на сообщение 'Подписаться на рассылку'.

    Фильтрует сообщения и отвечает только на 'Подписаться на рассылку',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с кнопкой 'Отписаться от рассылки'"""
    if await check_user_subscription(message.peer_id):
        await message.answer(
            "Вы уже подписаны", keyboard=await settings_keyboard(message.payload)
        )
    else:
        await subscribe_on_newsletter(message.peer_id, message.payload.split(":")[1][1:3])
        await message.answer(
            "Вы успешно подписались на уведомления, мы сообщим, если появится новое расписание",
            keyboard=await settings_keyboard(message.payload),
        )


@bot.on.private_message(
    text="Отписаться от рассылки", payload=school_payloads
)
async def unsubscribe_from_mailing_list(message: Message):
    """Функция для ответа на сообщение 'Отписаться от рассылки'.

    Фильтрует сообщения и отвечает только на 'Отписаться от рассылки',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с кнопкой 'Подписаться на рассылку'"""
    if await check_user_subscription(message.peer_id):
        await unsubscribe_on_newsletter(message.peer_id)
        await message.answer(
            "Вы успешно отписались от рассылки",
            keyboard=await settings_keyboard(message.payload),
        )
    else:
        await message.answer(
            "Вы не подписаны на рассылку",
            keyboard=await settings_keyboard(message.payload),
        )


@bot.on.private_message(text="Узнать расписание", payload=school_payloads)
async def choice_parallel(message: Message):
    """Функция для ответа на сообщение 'Узнать расписание'.

    Фильтрует сообщения и отвечает только на 'Узнать расписание',
    добавляет id пользователя в базу данных для оповещения о появлении нового расписания,
    возвращает текстовое сообщение и клавиатуру для выбора параллели."""
    if await check_school_and_class(message.peer_id, message.payload.split(":")[1][1:3]):
        school, class_ = await get_school_and_class(message.peer_id)
        file_path = await get_schedule_class(school, class_)
        photo = [
            await PhotoMessageUploader(bot.api).upload(file)
            for file in sorted(file_path)
        ]
        await message.answer(
            f"Расписание {class_}", attachment=photo, keyboard=await get_schedule_keyboard(message.payload)
        )
    else:
        await message.answer("Выберите вашу параллель", keyboard=await parallels_keyboard(message.payload))


@bot.on.private_message(text="Настройки", payload=school_payloads)
async def change_settings(message: Message):
    await message.answer("Переходим в раздел настроек", keyboard=await settings_keyboard(message.payload))


@bot.on.private_message(text="Запоминание класса", payload=school_payloads)
async def memory_class(message: Message):
    if not await check_class(message.peer_id):
        await message.answer("Хотите чтобы мы запомнили ваш класс?", keyboard=await memory_class_keyboard(message.payload))
    else:
        await message.answer("Хотите изменить данные о вашем классе?", keyboard=await change_class_keyboard(message.payload))


@bot.on.private_message(text=parallel, payload=school_payloads)
async def choice_class(message: Message):
    """Функция для ответа на сообщение, в котором указаны параллели от 5-х до 11-х классов.

    Фильтрует сообщения и отвечает только на парралель,
    генерирует клавиатуру взависимости от выбранной параллели,
    возвращает текстовое сообщение и клавиатуру для выбора класса."""
    await message.answer(
        "Выберите ваш класс",
        keyboard=await give_parallel(message.text.split()[0], message.payload),
    )


@bot.on.private_message(
    text="Удалить данные о моём классе", payload=school_payloads
)
async def del_class(message: Message):
    if await check_class(message.peer_id):
        await change_user_class(message.peer_id, "", "")
        await message.answer(
            "Все данные о вашем классе были удалены", keyboard=await settings_keyboard(message.payload)
        )
    else:
        await message.answer("Не ломайте бота, пожалуйста", keyboard=await settings_keyboard(message.payload))


@bot.on.private_message(text="Назад", payload=back1)
async def back(message: Message):
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer("Переходим в меню настроек", keyboard=await settings_keyboard(return_payload))


@bot.on.private_message(text="Назад", payload=back2)
async def back(message: Message):
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer("Переходим в главное меню", keyboard=await get_schedule_keyboard(return_payload))


@bot.on.private_message(text=all_classes_names, payload=school_payloads)
async def get_schedule(message: Message):
    """Функция для отправки фотографий с расписанием.

    Функция фильтрует сообщения и отвечает только на те, в которых указан класс из списка CLASSES_NAMES,
    возвращает изображение или изображения(взависимости от класса и дня недели) + текст."""
    payload = message.payload
    school = payload.split(":")[1][1:3]
    file_path = await get_schedule_class(school, message.text)
    photo = [
        await PhotoMessageUploader(bot.api).upload(file) 
        for file in sorted(file_path)
    ]
    await message.answer(
        f"Расписание {message.text}", attachment=photo, keyboard=await get_schedule_keyboard(message.payload)
    )


@bot.on.private_message(lev="Запомнить мой класс", payload=school_payloads)
async def class_memory(message: Message):
    if not await check_class(message.peer_id):
        await bot.state_dispenser.set(message.peer_id, States_memory_class.class_name, payload=message.payload)
        await message.answer("Введите номер вашего класса и букву в верхнем регистре без пробелов", keyboard=hide_keyboard)
    else:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Не ломайте бота, пожалуйста", keyboard=await settings_keyboard(message.payload))


@bot.on.private_message(state=States_memory_class.class_name)
async def get_class_name(message: Message):
    payload = message.state_peer.payload["payload"]
    school = payload.split(":")[1][1:3]
    if message.text in await classes_names(school):
        await change_user_class(message.peer_id, school, message.text)
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer(
            "Мы вас запомнили, теперь вам не нужно выбирать класс и параллель",
            keyboard=await settings_keyboard(payload),
        )
    else:
        await bot.state_dispenser.set(message.peer_id, States_memory_class.class_name, payload=payload)
        return "Вы ввели некорректные данные, попробуйте ещё раз"


@bot.on.chat_message(ChatActionRule("chat_invite_user"))
async def hi_handler(message: Message):
    await message.answer("Здравствуйте, я Джарвиз, рад работать в вашей беседе")


@bot.on.private_message(lev="Изменить класс", payload=school_payloads)
async def change_class(message: Message):
    if await check_class(message.peer_id):
        await bot.state_dispenser.set(message.peer_id, States_change_class.class_name, payload=message.payload)
        await message.answer("Введите номер вашего класса и букву в верхнем регистре без пробелов", keyboard=hide_keyboard)


@bot.on.private_message(state=States_change_class.class_name)
async def select_class(message: Message):
    payload = message.state_peer.payload["payload"]
    school = payload.split(":")[1][1:3]
    if message.text in await classes_names(school):
        await change_user_class(message.peer_id, school, message.text)       
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer("Вы успешно изменили класс", keyboard=await settings_keyboard(payload))
    else:
        await bot.state_dispenser.set(message.peer_id, States_change_class.class_name, payload=payload)
        return "Вы ввели некорректные данные, попробуйте ещё раз"


@bot.on.private_message(text="Назад", payload=back3)
async def back(message: Message):
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer("Выберите вашу параллель", keyboard=await parallels_keyboard(return_payload))


@bot.on.private_message(text="Назад", payload=school_payloads)
async def back(message: Message):
    await message.answer("Переходим к выбору учебного заведения", keyboard=kb_select_school)


@bot.on.private_message()
async def other(message: Message):
    """Функция для обработки сообщений, на которые не настроены фильтры"""
    await message.answer("Я вас не понимаю|nПожалуйста, воспользуйтесь клавиатурой")


def main():
    """Функция, отвечающая за запуск бота.

    Функция запускает код бота, а вызывает функцию для запуска парсера,
    создвёт доп. процесс."""
    create_table()
    bot.run_forever()
