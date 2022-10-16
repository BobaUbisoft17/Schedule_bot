"""Модуль для вспомогательных функций."""

import datetime


def get_date(string: str) -> str:
    """Поиск даты в строке."""
    string = string.replace("_", " ")
    for elem in string.split():
        if is_date(elem):
            return elem
    return None


def is_date(string: str) -> bool:
    """Проверка на соответствие шаблону."""
    try:
        datetime.datetime.strptime(string, "%d.%m.%y")
        return True
    except ValueError:
        return False
