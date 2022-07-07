"""Файл с клавиатурами."""

from typing import List

from vkbottle import Keyboard, KeyboardButtonColor, OpenLink, Text


all_schools = [
    "14",
    "40",
]

school_payloads = [{"cmd": "14"}, {"cmd": "40"}]

back1 = [{"cmd": "141"}, {"cmd": "401"}]

back2 = [{"cmd": "142"}, {"cmd": "402"}]

back3 = [{"cmd": "143"}, {"cmd": "403"}]

parallel = [
    "5 классы",
    "6 классы",
    "7 классы",
    "8 классы",
    "9 классы",
    "10 классы",
    "11 классы",
]

classes = {
    "14": {
        "5": "АБВГДЕЖ",
        "6": "АБВГДЕЖЗИК",
        "7": "АБВГДЕЖЗ",
        "8": "АБВГДЕЖЗ",
        "9": "АБВГДЕЖЗИКЛ",
        "10": "АБВ",
        "11": "АБВ",
    },
    "40": {
        "5": "АБВГДЕЖЗИК",
        "6": "АБВГДЕЖЗ",
        "7": "АБВГДЕЖ",
        "8": "АБВГДЕЖЗИКЛ",
        "9": "АБВГДЕ",
        "10": "АБ",
        "11": "АБ",
    },
}


all_classnames = [
    f"{number}{letter}"
    for school in all_schools
    for (number, letters) in classes[school].items()
    for letter in letters
]


async def classes_names(school: str) -> List[str]:
    """Функция для создания клавиатуры классов."""
    return [
        f"{number}{letter}"
        for (number, letters) in classes[school].items()
        for letter in letters
    ]


hide_keyboard = Keyboard()

kb_select_school = (
    Keyboard()
    .add(
        Text("МАОУ 'СОШ №14'", {"cmd": "14"}),
        color=KeyboardButtonColor.PRIMARY,
    )
    .row()
    .add(
        Text("МАОУ 'СОШ №40'", {"cmd": "40"}),
        color=KeyboardButtonColor.PRIMARY,
    )
)


async def get_schedule_keyboard(payload: str) -> Keyboard:
    """Фунция для создания клавиатуры главного меню."""
    return (
        Keyboard()
        .add(
            Text("Узнать расписание", payload),
            color=KeyboardButtonColor.POSITIVE,
        )
        .row()
        .add(Text("Настройки", payload), color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(
            OpenLink("https://vk.com/@schedulebot14-documentation", "Помощь"),
            color=KeyboardButtonColor.SECONDARY,
        )
        .row()
        .add(Text("Назад", payload), color=KeyboardButtonColor.PRIMARY)
    )


async def sub_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры подписки на рассыклу."""
    new_payload = payload[:-2] + "1" + payload[-2:]
    return (
        Keyboard()
        .add(
            Text("Подписаться на рассылку", payload),
            color=KeyboardButtonColor.POSITIVE,
        )
        .row()
        .add(Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY)
    )


async def unsub_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры отписку от рассылки."""
    new_payload = payload[:-2] + "1" + payload[-2:]
    return (
        Keyboard()
        .add(
            Text("Отписаться от рассылки", payload),
            color=KeyboardButtonColor.NEGATIVE,
        )
        .row()
        .add(Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY)
    )


async def memory_class_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры для меню 'Запоминание класса'."""
    new_payload = payload[:-2] + "1" + payload[-2:]
    return (
        Keyboard()
        .add(
            Text("Запомнить мой класс", payload),
            color=KeyboardButtonColor.POSITIVE,
        )
        .row()
        .add(Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY)
    )


async def change_class_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры для меню \
       изменения информации о классе пользователя."""
    new_paylaod = payload[:-2] + "1" + payload[-2:]
    return (
        Keyboard()
        .add(
            Text("Изменить класс", payload),
            color=KeyboardButtonColor.POSITIVE,
        )
        .row()
        .add(
            Text("Удалить данные о моём классе", payload),
            color=KeyboardButtonColor.NEGATIVE,
        )
        .row()
        .add(Text("Назад", new_paylaod), color=KeyboardButtonColor.PRIMARY)
    )


async def settings_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры для меню настроек."""
    new_payload = payload[:-2] + "2" + payload[-2:]
    return (
        Keyboard()
        .add(
            Text("Настроить уведомления", payload),
            color=KeyboardButtonColor.SECONDARY,
        )
        .row()
        .add(
            Text("Запоминание класса", payload),
            color=KeyboardButtonColor.SECONDARY,
        )
        .row()
        .add(Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY)
    )


async def parallels_keyboard(payload: str) -> Keyboard:
    """Функция для создания клавиатуры параллелей."""
    new_payload = payload[:-2] + "2" + payload[-2:]
    kb_choice_parallel = Keyboard()
    for i in range(len(parallel)):
        if (i + 1) % 3 == 0:
            kb_choice_parallel.row()
        kb_choice_parallel.add(
            Text(parallel[i], payload), color=KeyboardButtonColor.POSITIVE
        )
    kb_choice_parallel.row().add(
        Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY
    )
    return kb_choice_parallel


async def give_parallel(parallel: str, payload: str) -> Keyboard:
    """Функция для генерации клавиатуры классов определённой параллели."""
    school = payload.split(":")[1][1:3]
    new_payload = payload[:-2] + "3" + payload[-2:]
    kb_choice_class = Keyboard()
    count = 0
    for class_ in await classes_names(school):
        if parallel in class_:
            if count % 4 == 0 and count != 0:
                kb_choice_class.row()
            count += 1
            kb_choice_class.add(
                Text(class_, payload), color=KeyboardButtonColor.POSITIVE
            )
    kb_choice_class.row().add(
        Text("Назад", new_payload), color=KeyboardButtonColor.PRIMARY
    )
    return kb_choice_class
