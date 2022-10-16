import datetime


def get_date(string: str) -> str:
    string = string.replace("_", " ")
    for elem in string.split():
        if is_date(elem):
            return elem


def is_date(string: str) -> bool:
    try:
        datetime.datetime.strptime(string, "%d.%m.%y")
        return True
    except ValueError:
        return False
