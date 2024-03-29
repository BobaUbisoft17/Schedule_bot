"""Файл для чтения .csv файлов."""

import csv
import glob
import os
from dataclasses import dataclass
from typing import List, Tuple

from convert_text_to_image import Schedule


PATH = "schedule_tables/school"


def get_classes_schedules(school: str) -> List[Schedule]:
    """Получение расписаний всех классов из .csv файлов."""
    classes_schedules = []
    for file in _get_csv_files(school):
        schedules = _fetch_classes_schedules_from_csv(file)
        classes_schedules.extend(schedules)
        os.remove(file)
    return classes_schedules


def _get_csv_files(school: str) -> List[str]:
    """Полученеия .csv файлов в текущей директории."""
    csv_files = glob.glob(PATH + school + "/*.csv")
    return sorted(csv_files)


def _fetch_classes_schedules_from_csv(filepath: str) -> List[Schedule]:
    """Получение расписаний классов из .csv файла."""
    with open(filepath, encoding="utf-8") as f:
        schedule = list(csv.reader(f, delimiter=";"))

    classes_names_row, *schedule = schedule
    classes_names = _fetch_classes_names(classes_names_row)
    schedule_bells, schedule = _get_schedule_bells(schedule)
    classes_schedules = _split_schedule_by_classes(len(classes_names), schedule)

    return _join_classes_schedule_with_bells(
        classes_names, schedule_bells, classes_schedules
    )


def _fetch_classes_names(classes_names_row: List[str]) -> List[str]:
    """Извлечение названий классов."""
    classes_names = []
    for cell in classes_names_row[1:]:
        if cell != "":
            classes_names.append(cell.split()[0].split("(")[0])
    return classes_names


def _get_schedule_bells(schedule: List[List[str]]) -> Tuple[List[str], List[List[str]]]:
    """Получение расписания перемен."""
    schedule_bells = []
    for i in range(len(schedule)):
        schedule_bells.append(schedule[i][1])
        schedule[i] = schedule[i][2:]
    for i in range(len(schedule_bells)):
        true_bell = []
        if "\n" not in schedule_bells[i]:
            for bell in schedule_bells[i].split("-"):
                true_bell_schedule = []
                bell = bell.replace(":", ".")
                for time in bell.split("."):
                    if len(time) < 2 and time != "":
                        time = "0" + time
                    elif time == "":
                        time = "не указано"
                    true_bell_schedule.append(time)
                true_bell.append(".".join([i for i in true_bell_schedule]))
        if "\n" in schedule_bells[i]:
            for bell in schedule_bells[i].split("-\n"):
                true_bell_schedule = []
                bell = bell.replace(":", ".")
                for time in bell.split("."):
                    if len(time) < 2 and time != "":
                        time = "0" + time
                    elif time == "":
                        time = "не указано"
                    true_bell_schedule.append(time)
                true_bell.append(".".join([i for i in true_bell_schedule]))
        schedule_bells[i] = "-".join([i for i in true_bell])

    return schedule_bells, schedule


def _split_schedule_by_classes(
    classes_count: int, schedules: List[List[str]]
) -> List[List[str]]:
    """Распределение расписания по классам."""
    classes_schedules = []
    for i in range(classes_count):
        class_schedule = []
        for schedule in schedules:
            if ("классный час" in schedule or "Классный час" in schedule) and len(
                schedule
            ) == 1:
                schedule *= len(classes_count)
            if len(schedule) < classes_count and len(schedule) != 1:
                count = 0
                for lesson in schedule:
                    if lesson == "":
                        count += 1
                    else:
                        index = schedule.index(lesson)
                schedule = (
                    schedule[:index]
                    + [schedule[index] for _ in range(classes_count - count)]
                    + schedule[index:]
                )
            if schedule[i] == "" or schedule[i] == "-" or schedule[i] == ".":
                schedule[i] = "нет урока"
            class_schedule.append(schedule[i])
        classes_schedules.append(class_schedule)

    return classes_schedules


def _join_classes_schedule_with_bells(
    classes_schedules: list, bells: list, schedules: list
) -> List[Schedule]:
    """Объединение классов, звонков и расписания."""
    classes_schedules_with_bells = []
    for i in range(len(classes_schedules)):
        classes_schedules_with_bells.append(
            Schedule(classes_schedules[i], schedules[i], bells)
        )

    return classes_schedules_with_bells
