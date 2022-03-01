from types import TracebackType
from vkbottle import Keyboard, KeyboardButtonColor, Text, OpenLink


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
    "5": "АБВГДЕЖ",
    "6": "АБВГДЕЖЗИК",
    "7": "АБВГДЕЖЗ",
    "8": "АБВГДЕЖЗ",
    "9": "АБВГДЕЖЗИКЛ",
    "10": "АБВ",
    "11": "АБВ",
}

CLASSES_NAMES = [
    f"{number}{letter}" for (number, letters) in classes.items() for letter in letters
]


kb_get_schedule = (
    Keyboard(one_time=True)
    .add(
        Text("Узнать расписание", {"cmd": "get_schedule"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .row()
    .add(Text("Настройки", {"cmd": "settings"}), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(
        OpenLink(
            "https://vk.com/@schedulebot14-pomosch-v-poluchenii-raspisaniya", "Помощь"
        ),
        color=KeyboardButtonColor.SECONDARY,
    )
)

kb_subscribe_to_newsletter = (
    Keyboard()
    .add(
        Text("Подписаться на рассылку", {"cmd": "subscribe_on_newsletter"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .row()
    .add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.PRIMARY)
)


kb_unsubscribe_from_mailing_list = (
    Keyboard()
    .add(
        Text("Отписаться от рассылки", {"cmd": "unsubscribe_on_newsletter"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
    .row()
    .add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.PRIMARY)
)


kb_memory_class = (
    Keyboard(one_time=True)
    .add(
        Text("Запомнить мой класс", {"cmd": "memory_my_class"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .row()
    .add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.PRIMARY)
)


kb_change_class = (
    Keyboard(one_time=True)
    .add(
        Text("Изменить класс", {"cmd": "change_my_class"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    .row()
    .add(
        Text("Удалить данные о моём классе", {"cmd": "del_my_class"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
    .row().add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.PRIMARY)
)


kb_settings = (
    Keyboard()
    .add(
        Text("Настроить уведомления", {"cmd": "set_notifications"}),
        color=KeyboardButtonColor.SECONDARY,
    )
    .row()
    .add(
        Text("Запоминание класса", {"cmd": "set_memory_class"}),
        color=KeyboardButtonColor.SECONDARY,
    )
    .row()
    .add(Text("Назад", {"cmd": "back2"}), color=KeyboardButtonColor.PRIMARY)
)


kb_choice_parallel = Keyboard()
for i in range(len(parallel)):
    if (i + 1) % 3 == 0:
        kb_choice_parallel.row()
    kb_choice_parallel.add(
        Text(parallel[i], {"cmd": "parallel"}), color=KeyboardButtonColor.POSITIVE
    )
kb_choice_parallel.row().add(
    Text("Назад", {"cmd": "back3"}), color=KeyboardButtonColor.PRIMARY
)


kb_choice_class = Keyboard()


async def give_parallel(parallel):
    """Функция для генерации клавиатуры."""
    kb_choice_class = Keyboard(one_time=True)
    count = 0
    for class_ in CLASSES_NAMES:
        if parallel in class_:
            if count % 4 == 0 and count != 0:
                kb_choice_class.row()
            count += 1
            kb_choice_class.add(
                Text(class_, {"cmd": "class_"}), color=KeyboardButtonColor.POSITIVE
            )
    kb_choice_class.row().add(
        Text("Назад", {"cmd": "back4"}), color=KeyboardButtonColor.PRIMARY
    )
    return kb_choice_class
