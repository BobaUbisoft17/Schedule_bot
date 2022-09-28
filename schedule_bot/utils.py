import datetime 
from typing import List


def get_date(string: str) -> str:
    for elem in string.split():
        if is_date(elem):
            return elem

    for elem in string.split("_"):
        date = elem.split()[0]
        if is_date(elem.split()[0]):
            return date


def is_date(string: str) -> bool:
    try:
        datetime.datetime.strptime(string, "%d.%m.%y")
        return True
    except ValueError:
        return False