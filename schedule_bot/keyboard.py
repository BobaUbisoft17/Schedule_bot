from vkwave.bots.utils.keyboards.keyboard import ButtonColor, Keyboard


parallel = [
	"5 классы",
	"6 классы",
	"7 классы",
	"8 классы",
	"9 классы",
	"10 классы",
	"11 классы"
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
	f"{number}{letter}"
	for (number, letters) in classes.items()
	for letter in letters
]


kb_get_schedule = Keyboard(one_time=True)
kb_choice_parallel = Keyboard(one_time=True)
kb_choice_class = Keyboard(one_time=True)
kb_subscribe_to_newsletter = Keyboard(one_time=True)
kb_unsubscribe_from_mailing_list = Keyboard(one_time=True)


kb_get_schedule.add_text_button("Узнать расписание", color=ButtonColor.POSITIVE)
kb_get_schedule.add_row()
kb_get_schedule.add_text_button("Настроить уведомления", color=ButtonColor.SECONDARY)
kb_subscribe_to_newsletter.add_text_button("Подписаться на рассылку", color=ButtonColor.PRIMARY)
kb_subscribe_to_newsletter.add_row()
kb_subscribe_to_newsletter.add_text_button("назад", color=ButtonColor.NEGATIVE)
kb_unsubscribe_from_mailing_list.add_text_button("Отписаться от рассылки", color=ButtonColor.PRIMARY)
kb_unsubscribe_from_mailing_list.add_row()
kb_unsubscribe_from_mailing_list.add_text_button("назад", color=ButtonColor.NEGATIVE)


for i in range(len(parallel)):
	if (i + 1) % 3 == 0:
		kb_choice_parallel.add_row()
	kb_choice_parallel.add_text_button(parallel[i], color=ButtonColor.POSITIVE)



def give_parallel(parallel):
	"""Функция для генерации клавиатуры."""
	kb_choice_class = Keyboard(one_time=True)
	count = 0
	for class_ in CLASSES_NAMES:
		if parallel in class_:
			if count % 4 == 0 and count != 0:
				kb_choice_class.add_row()
			count += 1
			kb_choice_class.add_text_button(class_, color=ButtonColor.POSITIVE)
	return kb_choice_class