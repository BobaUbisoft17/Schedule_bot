class SubscriberRepository:
    """Хранилище подписчиков рассылки обновлений расписания."""

    def save(self, user_id: int):
        """Добавление пользователя в рассылку."""

    def get_all(self) -> List[int]:
        """Получение всех подписчиков рассылки."""

    def exists(self, user_id: int) -> bool:
        """Присутствует ли пользователь в рассылке."""

    def delete(self, user_id: int):
        """Удаление подписчика из рассылки."""
