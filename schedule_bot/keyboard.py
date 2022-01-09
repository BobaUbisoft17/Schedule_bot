from types import TracebackType
from vkbottle import Keyboard, KeyboardButtonColor, Text


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


kb_get_schedule = Keyboard(one_time=True)
kb_choice_parallel = Keyboard(one_time=True)
kb_choice_class = Keyboard(one_time=True)
kb_subscribe_to_newsletter = Keyboard(one_time=True)
kb_unsubscribe_from_mailing_list = Keyboard(one_time=True)
kb_memory_class = Keyboard(one_time=True)
kb_change_class = Keyboard(one_time=True)


kb_get_schedule.add(Text("Узнать расписание"), color=KeyboardButtonColor.POSITIVE)
kb_get_schedule.row()
kb_get_schedule.add(Text("Настроить уведомления"), color=KeyboardButtonColor.SECONDARY)
kb_get_schedule.row()
kb_get_schedule.add(Text("Настроить запоминание класса"), color=KeyboardButtonColor.SECONDARY)
kb_subscribe_to_newsletter.add(Text(
    "Подписаться на рассылку"), color=KeyboardButtonColor.PRIMARY
)
kb_subscribe_to_newsletter.row()
kb_subscribe_to_newsletter.add(Text("Назад"), color=KeyboardButtonColor.NEGATIVE)
kb_unsubscribe_from_mailing_list.add(Text(
    "Отписаться от рассылки"), color=KeyboardButtonColor.PRIMARY
)
kb_unsubscribe_from_mailing_list.row()
kb_unsubscribe_from_mailing_list.add(Text("Назад"), color=KeyboardButtonColor.NEGATIVE)


for i in range(len(parallel)):
    if (i + 1) % 3 == 0:
        kb_choice_parallel.row()
    kb_choice_parallel.add(Text(parallel[i]), color=KeyboardButtonColor.POSITIVE)


async def give_parallel(parallel):
    """Функция для генерации клавиатуры."""
    kb_choice_class = Keyboard(one_time=True)
    count = 0
    for class_ in CLASSES_NAMES:
        if parallel in class_:
            if count % 4 == 0 and count != 0:
                kb_choice_class.row()
            count += 1
            kb_choice_class.add(Text(class_, {"cmd": "class_"}), color=KeyboardButtonColor.POSITIVE)
    return kb_choice_class

kb_memory_class.add(Text("Запомнить мой класс"), color=KeyboardButtonColor.POSITIVE)
kb_change_class.add(Text("Изменить класс"), color=KeyboardButtonColor.POSITIVE)
kb_change_class.row()
kb_change_class.add(Text("Удалить данные о моём классе"), color=KeyboardButtonColor.NEGATIVE)
