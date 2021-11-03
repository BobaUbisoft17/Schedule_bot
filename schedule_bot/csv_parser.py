import csv
import glob
import os
from dataclasses import dataclass
from typing import List, Tuple


PATH = "*.csv"


@dataclass
class ClassSchedule:
    class_name: str
    schedule: str


def get_classes_schedules() -> List[ClassSchedule]:
    """Получение расписаний всех классов из .csv файлов."""
    classes_schedules = []
    for file in _get_csv_files(PATH):
        for table in _fetch_classes_schedules_from_csv(file):
            classes_schedules.append(
                ClassSchedule(
                    class_name=table[0],
                    schedule=table[-1],
                )
            )
        os.remove(file)

    return classes_schedules


def _get_csv_files(path: list) -> List[str]:
    """Полученеия .csv файлов в текущей директории."""
    csv_files = glob.glob(path)
    return csv_files


def _fetch_classes_schedules_from_csv(filepath: str) -> List[Tuple[str, str]]:
    """Получение расписаний классов из .csv файла."""
    with open(filepath, encoding="utf-8") as f:
        schedule = list(csv.reader(f, delimiter=";"))

    classes_names_row, *schedule = schedule
    classes_names = _fetch_classes_names(classes_names_row)
    schedule_bells, schedule = _get_schedule_bells(schedule)
    classes_schedules = _split_schedule_by_classes(
        len(classes_names), schedule
    )

    return _join_classes_schedule_with_bells(
        classes_names, schedule_bells, classes_schedules
    )


def _fetch_classes_names(classes_names_row: list):
    """Извлечение названий классов."""
    return [
        cell.replace(" ", "")
        for cell in classes_names_row
        if "(" in cell or ")" in cell
    ]


def _get_schedule_bells(schedule: list):
    """Получение расписания перемен."""
    schedule_bells = []
    for i in range(len(schedule)):
        schedule_bells.append(schedule[i][1])
        schedule[i] = schedule[i][2:]
    return schedule_bells, schedule


def _split_schedule_by_classes(classes_count: int, schedules: list):
    """Распределение расписания по классам."""
    classes_schedules = []
    for i in range(classes_count):
        class_schedule = []
        for schedule in schedules:
            if (
                ("классный час" in schedule or "Классный час" in schedule)
                and len(schedule) == 1
            ):
                schedule *= i
            if schedule[i] == "" or schedule[i] == "-":
                schedule[i] = "окно"
            class_schedule.append(schedule[i])
        classes_schedules.append(class_schedule)

    return classes_schedules


def _join_classes_schedule_with_bells(
    classes_schedules: list, bells: list, schedules: list
):
    """Объединение классов, звонков и расписания."""
    classes_schedules_with_bells = []
    for i in range(len(classes_schedules)):
        full_schedule = classes_schedules[i] + "\n"
        for bell, schedule in zip(bells, schedules[i]):
            full_schedule += f"{bell} {schedule}\n"
        classes_schedules_with_bells.append(
            [classes_schedules[i], full_schedule]
        )

    return classes_schedules_with_bells
