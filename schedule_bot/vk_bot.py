from config import VKBOTTOKEN
import logging
from vkwave.bots import SimpleLongPollBot, SimpleBotEvent
from vkwave.bots.core.dispatching import filters
from keyboard import kb_get_schedule, kb_choice_parallel, parallel, CLASSES_NAMES, give_parallel
from vkwave.bots.utils.uploaders import PhotoUploader
from file_service import get_schedule_class
from database_users import add_id
from schedule_parser import parse
import asyncio

logging.basicConfig(level=logging.INFO)
# Создаём объект бота
bot = SimpleLongPollBot(tokens=VKBOTTOKEN, group_id=209208856)
CLASSES_NAMES = [i.lower() for i in CLASSES_NAMES]


@bot.message_handler(filters.TextFilter("начать"))
async def greetings(event: SimpleBotEvent) -> str:
    """Функция для ответа на сообщение 'Начать'."""

    """Фильтрует сообщения и отвечает только на 'Начать',
       возвращает текстовое сообщение и клавиатуру."""
    await event.answer("Здравствуйте!!!", keyboard=kb_get_schedule.get_keyboard())


@bot.message_handler(filters.TextFilter("узнать расписание"))
async def choice_class(event: SimpleBotEvent) -> str:
    """Функция для ответа на сообщение 'Узнать расписание'."""

    """Фильтрует сообщения и отвечает только на 'Узнать расписание',
       добавляет id пользователя в базу данных для оповещения о появлении нового расписания,
       возвращает текстовое сообщение и клавиатуру для выбора параллели."""
    add_id(event.object.object.message.peer_id)
    await event.answer("Выберите вашу параллель", keyboard=kb_choice_parallel.get_keyboard())


@bot.message_handler(filters.TextFilter(parallel))
async def choice_parallel(event: SimpleBotEvent):
    """Функция для ответа на сообщение, в котором указаны параллели от 5-х до 11-х классов."""

    """Фильтрует сообщения и отвечает только на парралель,
       генерирует клавиатуру взависимости от выбранной параллели,
       возвращает текстовое сообщение и клавиатуру для выбора класса."""
    await event.answer("Выберите ваш класс", keyboard=give_parallel(event.object.object.message.text.split()[0]).get_keyboard())


@bot.message_handler(filters.TextFilter(CLASSES_NAMES))
async def get_schedule(event: SimpleBotEvent):
    """Функция для отправки фотографий с расписанием."""

    """Функция фильтрует сообщения и отвечает тольок на те, в которых указан класс из списка CLASSES_NAMES,
       возвращает изображение или изображения(взависимости от класса и дня недели) + текст."""
    file_path = get_schedule_class(event.object.object.message.text)
    peer_id = event.object.object.message.peer_id
    if len(file_path) == 1:
        file_path = file_path[0]
        attachment = await PhotoUploader(bot.api_context).get_attachment_from_path(
            peer_id=peer_id, 
            file_path=file_path
        )
    else:
        attachment = await PhotoUploader(bot.api_context).get_attachments_from_paths(
            peer_id=peer_id,
            file_paths=file_path
        )
    await event.answer(message=f"Расписание {event.object.object.message.text}", attachment=attachment, keyboard=kb_get_schedule.get_keyboard())


def main():
    """Функция, отвечающая за запуск бота."""

    """Функция запускает код бота, а вызывает функцию для запуска парсера,
       создвёт доп. процесс."""
    loop = asyncio.get_event_loop_policy().get_event_loop()
    add_parser_to_loop(loop)
    bot.run_forever(loop=loop)

def add_parser_to_loop(loop):
    loop.create_task(parse(bot))


main()
"""if __name__ == '__main__':
    while True:
        asyncio.run(parse())"""

