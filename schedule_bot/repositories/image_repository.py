from pathlib import Path

from PIL import Image


class ImageRepository:
    """Хранилище изображений расписаний классов.

    Обёртка над папкой с изображениями расписаний классов.
    """

    PATH = Path("images")

    def delete_all(self):
        """Удаление всех изображений."""
        for file in self.PATH.iterdir():
            file.unlink()

    def exists(self, filename: str) -> bool:
        """Существует ли изображение с данным названием файла."""
        return self.PATH.joinpath(filename).exists()

    def save(self, filename: str, image: Image):
        """Сохранение изображения."""
        image.save(self.PATH.joinpath(filename))
