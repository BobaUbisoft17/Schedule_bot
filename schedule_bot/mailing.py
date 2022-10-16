"""Модуль для рассылки уведомлений."""

from vkbottle import CodeException
from vkbottle.bot import Bot

from db_users import get_users_id, unsubscribe_on_newsletter


status_messages = {
    "Update": "Появилось обновлённое расписание",
    "New": "Появилось новое расписание",
}


async def mailing_list(bot: Bot, status: str, school: str) -> None:
    """Функция для оповещение пользователей о новом/обновлённом расписании."""
    message = status_messages[status]
    for user_id in await get_users_id(school):
        try:
            await bot.api.messages.send(user_id=user_id, message=message, random_id=0)
        except CodeException:
            await unsubscribe_on_newsletter(user_id)
