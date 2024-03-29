"""Модуль для вспомогательных функций."""

import datetime


def get_date(string: str) -> str:
    """Поиск даты в строке."""
    string = string.replace("_", " ")
    string = string[::-1].replace(".", " ", 1)[::-1]
    print(string)
    for elem in string.split():
        if is_short_date(elem):
            return elem
        elif is_long_date(elem):
            return elem[:-4] + elem[-2:]
        elif without_year(elem):
            year = datetime.datetime.now().year
            return f"{elem}.{year % 100}"
    return None


def is_short_date(string: str) -> bool:
    """Проверка на соответствие короткому шаблону."""
    try:
        datetime.datetime.strptime(string, "%d.%m.%y")
        return True
    except ValueError:
        return False

def is_long_date(string: str) -> bool:
    """Проверка на соответствие длинному шаблону."""
    try:
        datetime.datetime.strptime(string, "%d.%m.%Y")
        return True
    except:
        return False
    
def without_year(string: str) -> bool:
    try:
        datetime.datetime.strptime(string, "%d.%m")
        return True
    except ValueError:
        return False
