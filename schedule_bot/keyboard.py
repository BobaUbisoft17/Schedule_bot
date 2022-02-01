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


kb_get_schedule = Keyboard()
kb_choice_parallel = Keyboard()
kb_choice_class = Keyboard()
kb_subscribe_to_newsletter = Keyboard()
kb_unsubscribe_from_mailing_list = Keyboard()
kb_memory_class = Keyboard(one_time=True)
kb_change_class = Keyboard(one_time=True)
kb_settings = Keyboard()


kb_get_schedule.add(Text("Узнать расписание", {"cmd": "get_schedule"}), color=KeyboardButtonColor.POSITIVE)
kb_get_schedule.row()
kb_get_schedule.add(Text("Настройки", {"cmd": "settings"}), color=KeyboardButtonColor.SECONDARY)
kb_get_schedule.row()
kb_get_schedule.add(Text("Помощь", {"cmd": "help"}), color=KeyboardButtonColor.SECONDARY)
kb_settings.add(Text("Настроить уведомления", {"cmd": "set_notifications"}), color=KeyboardButtonColor.SECONDARY)
kb_settings.row()
kb_settings.add(Text("Настроить запоминание класса", {"cmd" : "set_memory_class"}), color=KeyboardButtonColor.SECONDARY)
kb_settings.row()
kb_settings.add(Text("Назад", {"cmd": "back2"}), color=KeyboardButtonColor.NEGATIVE)
kb_subscribe_to_newsletter.add(Text(
    "Подписаться на рассылку", {"cmd": "subscribe_on_newsletter"}), color=KeyboardButtonColor.PRIMARY
)
kb_subscribe_to_newsletter.row()
kb_subscribe_to_newsletter.add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.NEGATIVE)
kb_unsubscribe_from_mailing_list.add(Text(
    "Отписаться от рассылки", {"cmd": "unsubscribe_on_newsletter"}), color=KeyboardButtonColor.PRIMARY
)
kb_unsubscribe_from_mailing_list.row()
kb_unsubscribe_from_mailing_list.add(Text("Назад", {"cmd": "back1"}), color=KeyboardButtonColor.NEGATIVE)


for i in range(len(parallel)):
    if (i + 1) % 3 == 0:
        kb_choice_parallel.row()
    kb_choice_parallel.add(Text(parallel[i], {"cmd": "parallel"}), color=KeyboardButtonColor.POSITIVE)


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

kb_memory_class.add(Text("Запомнить мой класс", {"cmd": "memory_my_class"}), color=KeyboardButtonColor.POSITIVE)
kb_change_class.add(Text("Изменить класс", {"cmd": "change_my_class"}), color=KeyboardButtonColor.POSITIVE)
kb_change_class.row()
kb_change_class.add(Text("Удалить данные о моём классе", {"cmd": "del_my_class"}), color=KeyboardButtonColor.NEGATIVE)


BOT_SUPPORT = (
    "Помощь в получении расписания:\n"
    "\tЧтобы получить расписание, вам необходимо выполнить следующие действия:\n"
    "\t\t1. Нажать на клавиатуре кнопку “Узнать расписание”\n"
    "\t\t2. Выбрать вашу параллель среди представленных\n"
    "\t\t3. Выбрать ваш класс среди представленных\n\n\n"
    "Запоминание, изменение, удаление информации о вашем классе:\n"
    "\tЕсли вам не нравится выбирать каждый раз параллель и класс, и вы хотите получать расписание по нажатию одной кнопки, то выполните следующие действия:\n"  
    "\t\t1. Нажать на клавиатуре кнопку “Настройки”\n"
    "\t\t2. Выбрать пункт “Настроить запоминание класса”\n" 
    "\t\t3. Нажать на клавиатуре кнопку “Запомнить мой класс”\n" 
    "\t\t4. Ввести название своего класса без пробелов в верхнем регистре (Пример: 9А)\n\n" 
    "\tЕсли вы хотите изменить свой класс, выполните следующие действия:\n" 
    "\t\t1. Нажать на клавиатуре кнопку “Настройки”\n" 
    "\t\t2. Выбрать пункт “Настроить запоминание класса”\n" 
    "\t\t3. Нажать на клавиатуре кнопку “Изменить класс”\n" 
    "\t\t4. Ввести название своего класса без пробелов в верхнем регистре (Пример: 9А)\n\n" 
    "\tЕсли вы хотите удалить данные о выбранном вами классе, выполните следующие действия:\n" 
    "\t\t1. Нажать на клавиатуре кнопку “Настройки”\n" 
    "\t\t2. Выбрать пункт “Настроить запоминание класса”\n" 
    "\t\t3. Нажать на клавиатуре кнопку “Удалить данные о моём классе”\n\n\n" 
    "Управление уведомлениями:\n" 
    "\tЕсли вы хотите получать уведомления о появлении нового расписания на сайте школы, выполните следующие действия:\n" 
    "\t\t1. Нажать на клавиатуре кнопку “Настройки”\n" 
    "\t\t2. Выбрать пункт “Настроить уведомления”\n"
    "\t\t3. Нажать на клавиатуре на кнопку “Подписаться на рассылку”\n\n" 
    "\tЕсли вы хотите отписаться от рассылки, выполните следующие действия:\n" 
    "\t\t1. Нажать на клавиатуре кнопку “Настройки”\n" 
    "\t\t2. Выбрать пункт “Настроить уведомления”\n" 
    "\t\t3. Нажать на клавиатуре на кнопку “Отписаться от рассылки”\n\n\n" 
    "Действия при ошибке в работе бота:\n" 
    "\tЕсли вы столкнулись с ошибкой, которая нарушила работу бота, попробуйте ввести вручную слово “Начать”. Если ошибка не ушла, настоятельно просим перейти по ссылке https://vk.com/topic-209208856_48107960 и описать вашу проблему. "
)