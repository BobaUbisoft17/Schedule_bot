"""Файл для поиска фотографий класса определённой школы."""

import glob
from typing import List

# Словарь для определения директории школы
schoolpathes = {
    "14": "school14",
    "40": "school40",
}


def get_schedule_class(school: str, classname: str) -> List[str]:
    """Функция для поиска изображений расписания для отдельного класса."""
    return [
        file
        for file in glob.glob(
            ("schedule_image/" + schoolpathes[school] + "/*.jpg")
        )
        if classname in file
    ]
