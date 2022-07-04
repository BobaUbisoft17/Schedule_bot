"""Файл для получения расписания из .xls файлов"""

from convert_text_to_image import Schedule
from typing import List, Tuple
import xlrd
import glob


PATH = "schedule_tables/school40/"


def get_files() -> List[str]:
    """Фунция для получения названий .xls файлов в директории"""
    xls_files = glob.glob(PATH + "*.xls")
    return xls_files


def get_classes_schedules() -> List[Schedule]:
    """Функция для записи расписания в dataclass"""
    classes_schedules = []
    for file in get_files():
        for table in read_file(file):
            classes_schedules.append(
                Schedule(class_name=table[0], schedule=table[1], bells=table[2])
            )
    return classes_schedules


def read_file(file: str) -> List[Tuple[str, List[str], List[str]]]:
    """Функция для считывания файла и сортировки данных"""
    book = xlrd.open_workbook(file)
    sheet = book.sheet_by_index(0)
    row_classes = [class_.upper() for class_ in sheet.row_values(2)]
    classes = get_classnames(sheet.row_values(2)[3:])
    class_and_amount_cols = get_class_and_amount_cols(classes, row_classes)
    rows_lessons = get_lessons(sheet)
    sorted_schedule = get_sorted_schedule(class_and_amount_cols, rows_lessons)
    schedule_bells = get_schedule_bells(sheet)
    return group_schedule_classname_bells(
        classes, sorted_schedule, schedule_bells
    )


def get_classnames(row_classnames: List[str]) -> List[str]:
    """Функция для получения названий классов"""
    classnames = [class_.upper() for class_ in set(row_classnames)]
    classnames.remove("")
    return sorted(classnames, key=lambda x: (int(x[:-1]), x[-1]))


def get_class_and_amount_cols(classnames: List[str], row_classes: List[str]) -> List[Tuple[str, int]]:
    """Функция для получения информации о количестве столбцов, которые принадлежат отдельному классу"""
    class_and_amount_cols = []
    for class_ in classnames:
        count_cols = 1
        index = row_classes.index(class_)
        while len(row_classes) - 1 >= index + 1 and row_classes[index + 1] == "":
            count_cols += 1
            index += 1
        class_and_amount_cols.append([class_, count_cols])
    return class_and_amount_cols


def get_lessons(sheet) -> List[List[str]]:
    """Функция для получения строк с расписанием"""
    schedules = []
    for row in range(3, sheet.nrows):
        schedules.append(sheet.row_values(row)[3:])
    return schedules


def collect_schedule(rows_schedule: List[List[str]], amount_cols: int, index: int) -> List[str]:
    """Функция для сборки расписания по классам"""
    schedule = []
    if len(rows_schedule) % 2 == 0:
        len_rows = len(rows_schedule)
    else:
        len_rows = len(rows_schedule) - 1
    for i in range(0, len_rows, 2):
        lesson = rows_schedule[i][index]
        if lesson == "":
            lesson = "нет урока"
        parlors = []
        for parlor in rows_schedule[i + 1][index: index + amount_cols]:
            if parlor != "" and parlor != "/":
                if type(parlor) is float:
                    parlors.append(str(int(parlor)))
                else:
                    parlors.append(parlor)
        schedule.append(f"{lesson.lower()} {', '.join(parlors)}")
    if len(rows_schedule) % 2 != 0:
        schedule.append("нет урока")
    return schedule


def get_sorted_schedule(class_and_amount_cols: List[Tuple[str, int]], schedules: List[List[str]]) -> List[List[str]]:
    """Функция для сортировки расписания для классов"""
    schedules_and_office = []
    index = 0
    for class_ in class_and_amount_cols:
        schedules_and_office.append(
            collect_schedule(schedules, class_[-1], index)
        )
        index += class_[-1]
    return schedules_and_office


def get_schedule_bells(sheet) -> List[str]:
    """Функция для получения расписания звонков из файла"""
    bells = []
    list_bells = sheet.col_values(2)
    for element in list_bells[3:]:
        if element != "":
            bells.append(element.replace(" ", ""))
    return bells


def group_schedule_classname_bells(classnames: List[str], schedules: List[str], bells: List[str]) -> List[Tuple[str, List[str], List[str]]]:
    """Функция для объединения звонков, классов и уроков"""
    group_schedule = []
    for i in range(len(classnames)):
        group_schedule.append([classnames[i], schedules[i], bells])
    return group_schedule
