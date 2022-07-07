"""Файл для поиска фотографий класса определённой школы."""

import glob
from typing import List


dict_of_schoolpath = {
    "14": "school14",
    "40": "school40",
}


def get_schedule_class(school: str, classname: str) -> List[str]:
    """Функция для поиска изображений расписания для отдельного класса."""
    return [
        file
        for file in glob.glob(
            ("schedule_image/" + dict_of_schoolpath[school] + "/*.jpg")
        )
        if classname in file
    ]
