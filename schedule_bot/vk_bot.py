"""Файл для работы с VK."""

import asyncio
import logging
import os

from db_users import (
    add_id,
    change_user_class,
    check_class,
    check_school_and_class,
    check_user_subscription,
    create_table,
    get_school_and_class,
    subscribe_on_newsletter,
    unsubscribe_on_newsletter,
)
from file_service import get_schedule_class
from keyboard import (
    all_classes_names,
    back1,
    back2,
    back3,
    change_class_keyboard,
    classes_names,
    get_schedule_keyboard,
    give_parallel,
    hide_keyboard,
    kb_select_school,
    memory_class_keyboard,
    parallel,
    parallels_keyboard,
    school_payloads,
    settings_keyboard,
    sub_keyboard,
    unsub_keyboard,
)
from schedule_parser14 import parse14
from schedule_parser40 import parse40

from vkbottle import BaseStateGroup, PhotoMessageUploader
from vkbottle.bot import Bot, Message


class States_memory_class(BaseStateGroup):
    """Класс для запоминания класса пользователя."""

    class_name = 0


class States_change_class(BaseStateGroup):
    """Класс для изменения класса пользователя."""

    class_name = 0


bot = Bot(token=os.getenv("VKBOTTOKEN"))
bot.loop_wrapper.add_task(parse14(bot))
bot.loop_wrapper.add_task(parse40(bot))
logging.basicConfig(level=logging.INFO)


@bot.on.private_message(text="Начать")
async def hi_handler(message: Message) -> None:
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


@bot.on.private_message(
    text=["МАОУ 'СОШ №14'", "МАОУ 'СОШ №40'"], payload=school_payloads
)
async def home_space(message: Message) -> None:
    """Функция для возвращения клавиатуры с фильтром школы.

    Возвращает клавиатуру, в payload которой прописан фильтр выбранной школы
    """
    await message.answer(
        "Переходим в главное меню",
        keyboard=await get_schedule_keyboard(message.payload),
    )


@bot.on.private_message(text="Настроить уведомления", payload=school_payloads)
async def customize_notifications(message: Message) -> None:
    """Функция для ответа на сообщение 'Настроить уведомления'.

    Фильтрует сообщения и отвечает только на 'Настроить уведомления',
    если пользователя нет в базе данных, то возвращает текстовое сообщение и
    клавиатуру с кнопкой 'Подписаться на рассылку',
    иначе возвращает текстовое сообщение и клавиатуру с кнопкой
    'Отписаться от рассылки'
    """
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
async def subscribe_newsletter(message: Message) -> None:
    """Функция для ответа на сообщение 'Подписаться на рассылку'.

    Фильтрует сообщения и отвечает только на 'Подписаться на рассылку',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с кнопкой 'Отписаться от рассылки'
    """
    if await check_user_subscription(message.peer_id):
        await message.answer(
            "Вы уже подписаны",
            keyboard=await settings_keyboard(message.payload)
        )
    else:
        await subscribe_on_newsletter(
            message.peer_id, message.payload.split(":")[1][1:3]
        )
        await message.answer(
            "Вы успешно подписались на уведомления, \
мы сообщим, если появится новое расписание",
            keyboard=await settings_keyboard(message.payload),
        )


@bot.on.private_message(text="Отписаться от рассылки", payload=school_payloads)
async def unsubscribe_from_mailing_list(message: Message) -> None:
    """Функция для ответа на сообщение 'Отписаться от рассылки'.

    Фильтрует сообщения и отвечает только на 'Отписаться от рассылки',
    возвращает текстовое сообщение, зависящие от наличия пользователя в бд и
    клавиатуру с меню настроек
    """
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
async def choice_parallel(message: Message) -> None:
    """Функция для ответа на сообщение 'Узнать расписание'.

    Фильтрует сообщения и отвечает только на 'Узнать расписание',
    добавляет id пользователя в базу данных для оповещения о
    появлении нового расписания, возвращает текстовое сообщение
    и клавиатуру для выбора параллели.
    """
    if await check_school_and_class(
        message.peer_id, message.payload.split(":")[1][1:3]
    ):
        school, class_ = await get_school_and_class(message.peer_id)
        file_path = await get_schedule_class(school, class_)
        photo = [
            await PhotoMessageUploader(bot.api).upload(file)
            for file in sorted(file_path)
        ]
        if len(photo) != 0:
            await message.answer(
                f"Расписание {class_}",
                attachment=photo,
                keyboard=await get_schedule_keyboard(message.payload),
            )
        else:
            await message.answer(
                message="Для вашего класса расписание не найдено",
                keyboard=await get_schedule_keyboard(message.payload),
            )
    else:
        await message.answer(
            "Выберите вашу параллель",
            keyboard=await parallels_keyboard(message.payload),
        )


@bot.on.private_message(text="Настройки", payload=school_payloads)
async def change_settings(message: Message) -> None:
    """Функция для перехода в раздел настроек."""
    await message.answer(
        "Переходим в раздел настроек",
        keyboard=await settings_keyboard(message.payload)
    )


@bot.on.private_message(text="Запоминание класса", payload=school_payloads)
async def memory_class(message: Message) -> None:
    """Функция для проверки id-пользователя в БД.

    Берёт id-пользователя и в зависимости от того есть
    ли пользователь в БД возвращает клавиатуру.
    """
    if not await check_class(message.peer_id):
        await message.answer(
            "Хотите чтобы мы запомнили ваш класс?",
            keyboard=await memory_class_keyboard(message.payload),
        )
    else:
        await message.answer(
            "Хотите изменить данные о вашем классе?",
            keyboard=await change_class_keyboard(message.payload),
        )


@bot.on.private_message(text=parallel, payload=school_payloads)
async def choice_class(message: Message) -> None:
    """Функция для ответа на сообщение, \
    в котором указаны параллели от 5-х до 11-х классов.

    Фильтрует сообщения и отвечает только на парралель,
    генерирует клавиатуру в зависимости от выбранной параллели,
    возвращает текстовое сообщение и клавиатуру для выбора класса.
    """
    await message.answer(
        "Выберите ваш класс",
        keyboard=await give_parallel(message.text.split()[0], message.payload),
    )


@bot.on.private_message(
    text="Удалить данные о моём классе",
    payload=school_payloads
)
async def del_class(message: Message) -> None:
    """Функция для удаления данных о классе пользователя из БД.

    Берёт id-пользователя и удаляет данные по нему данные о классе.
    """
    if await check_class(message.peer_id):
        await change_user_class(message.peer_id, "", "")
        await message.answer(
            "Все данные о вашем классе были удалены",
            keyboard=await settings_keyboard(message.payload),
        )
    else:
        await message.answer(
            "Не ломайте бота, пожалуйста",
            keyboard=await settings_keyboard(message.payload),
        )


@bot.on.private_message(text="Назад", payload=back1)
async def back1(message: Message) -> None:
    """Функция для возвращения к меню настроек.

    Возвращает пользователя из меню 'Запоминание класса'
    или 'Подписаться на рассылку' в меню настроек.
    """
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer(
        "Переходим в меню настроек",
        keyboard=await settings_keyboard(return_payload)
    )


@bot.on.private_message(text="Назад", payload=back2)
async def back2(message: Message) -> None:
    """Функция для возвращения в главное меню.

    Возвращает пользователя из меню меню настроек в главное меню.
    """
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer(
        "Переходим в главное меню",
        keyboard=await get_schedule_keyboard(return_payload)
    )


@bot.on.private_message(text=all_classes_names, payload=school_payloads)
async def get_schedule(message: Message) -> None:
    """Функция для отправки фотографий с расписанием.

    Функция фильтрует сообщения и отвечает только на те,
    в которых указан класс из списка CLASSES_NAMES,
    возвращает изображение или
    изображения(взависимости от класса и дня недели) + текст.
    """
    payload = message.payload
    school = payload.split(":")[1][1:3]
    file_path = await get_schedule_class(school, message.text)
    photo = [
        await PhotoMessageUploader(bot.api).upload(file)
        for file in sorted(file_path)
    ]
    if len(photo) != 0:
        await message.answer(
            f"Расписание {message.text}",
            attachment=photo,
            keyboard=await get_schedule_keyboard(message.payload),
        )
    else:
        await message.answer(
            message="Для вашего класса расписание не найдено",
            keyboard=await get_schedule_keyboard(message.payload),
        )


@bot.on.private_message(lev="Запомнить мой класс", payload=school_payloads)
async def class_memory(message: Message) -> None:
    """Функция для запоминания класса пользователя.

    Берёт id-пользователя и в соответсвующем поле
    БД присваивает класс, выбранный пользователем.
    Запоминание класса сделано через машину состояний.
    """
    if not await check_class(message.peer_id):
        await bot.state_dispenser.set(
            message.peer_id,
            States_memory_class.class_name,
            payload=message.payload
        )
        await message.answer(
            "Введите номер вашего класса и букву в \
верхнем регистре без пробелов",
            keyboard=hide_keyboard,
        )
    else:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer(
            "Не ломайте бота, пожалуйста",
            keyboard=await settings_keyboard(message.payload),
        )


@bot.on.private_message(state=States_memory_class.class_name)
async def get_class_name(message: Message) -> None:
    """Функция, дополняющая предыдущию."""
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
        await bot.state_dispenser.set(
            message.peer_id, States_memory_class.class_name, payload=payload
        )
        await message.answer(
            "Вы ввели некорректные данные, попробуйте ещё раз"
        )


@bot.on.private_message(lev="Изменить класс", payload=school_payloads)
async def change_class(message: Message) -> None:
    """Функция для изменения данных о классе пользователя.

    Берёт id-пользователя и меняет класс в поле класса.
    Выполнена через машину состояний.
    """
    if await check_class(message.peer_id):
        await bot.state_dispenser.set(
            message.peer_id,
            States_change_class.class_name,
            payload=message.payload
        )
        await message.answer(
            "Введите номер вашего класса и букву \
в верхнем регистре без пробелов",
            keyboard=hide_keyboard,
        )


@bot.on.private_message(state=States_change_class.class_name)
async def select_class(message: Message) -> None:
    """Функция, дополняющая предыдущию."""
    payload = message.state_peer.payload["payload"]
    school = payload.split(":")[1][1:3]
    if message.text in await classes_names(school):
        await change_user_class(message.peer_id, school, message.text)
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer(
            "Вы успешно изменили класс",
            keyboard=await settings_keyboard(payload)
        )
    else:
        await bot.state_dispenser.set(
            message.peer_id, States_change_class.class_name, payload=payload
        )
        await message.answer(
            "Вы ввели некорректные данные, попробуйте ещё раз"
        )


@bot.on.private_message(text="Назад", payload=back3)
async def back3(message: Message) -> None:
    """Функция для возвращения к меню выбора параллели.

    Возвращает пользователя из меню выбора класса в меню выбора параллели.
    """
    payload = message.payload
    return_payload = payload[:-3] + payload[-2:]
    await message.answer(
        "Выберите вашу параллель",
        keyboard=await parallels_keyboard(return_payload)
    )


@bot.on.private_message(text="Назад", payload=school_payloads)
async def back4(message: Message) -> None:
    """Функция для возвращения к меню выбора учебного заведения.

    Возвращает пользователя из главного меню к меню выбора учебного заведения.
    """
    await message.answer(
        "Переходим к выбору учебного заведения", keyboard=kb_select_school
    )


@bot.on.private_message()
async def other(message: Message) -> None:
    """Функция для обработки сообщений, на которые не настроены фильтры."""
    await message.answer(
        "Я вас не понимаю.\nПожалуйста, воспользуйтесь клавиатурой"
    )


def create_loop() -> None:
    """Функция для создания цикла событий."""
    return asyncio.get_event_loop_policy().get_event_loop()


def main() -> None:
    """Функция, отвечающая за запуск бота.

    Функция запускает код бота, а вызывает функцию для запуска парсера,
    создвёт доп. процесс.
    """
    try:
        for dir1 in ["schedule_image", "schedule_tables"]:
            for dir2 in ["school14", "school40"]:
                os.makedirs(os.path.join(dir1, dir2))
    except FileExistsError:
        pass

    create_loop().run_until_complete(create_table())
    bot.run_forever()
