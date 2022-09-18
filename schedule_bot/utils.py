import datetime 
from typing import List


def get_date(list_string: List[str]) -> str:
    for string in list_string:
        if is_date(string):
            return string


def is_date(string: str) -> bool:
    try:
        datetime.datetime.strptime(string, "%d.%m.%y")
        return True
    except ValueError:
        return False