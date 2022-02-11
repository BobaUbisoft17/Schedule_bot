import csv
import glob
import os
from dataclasses import dataclass
from typing import List, Tuple


PATH = "schedule_tables/*.csv"


@dataclass
class ClassSchedule:
    class_name: str
    schedule: list
    bells: list


async def get_classes_schedules() -> List[ClassSchedule]:
    """Получение расписаний всех классов из .csv файлов."""
    classes_schedules = []
    for file in await _get_csv_files(PATH):
        for table in await _fetch_classes_schedules_from_csv(file):
            classes_schedules.append(
                ClassSchedule(class_name=table[0], schedule=table[1], bells=table[-1])
            )
        os.remove(file)
    return classes_schedules


async def _get_csv_files(path: list) -> List[str]:
    """Полученеия .csv файлов в текущей директории."""
    csv_files = glob.glob(path)
    return sorted(csv_files)


async def _fetch_classes_schedules_from_csv(filepath: str) -> List[Tuple[str, str]]:
    """Получение расписаний классов из .csv файла."""
    with open(filepath, encoding="utf-8") as f:
        schedule = list(csv.reader(f, delimiter=";"))

    classes_names_row, *schedule = schedule
    classes_names = await _fetch_classes_names(classes_names_row)
    schedule_bells, schedule = await _get_schedule_bells(schedule)
    classes_schedules = await _split_schedule_by_classes(len(classes_names), schedule)

    return await _join_classes_schedule_with_bells(
        classes_names, schedule_bells, classes_schedules
    )


async def _fetch_classes_names(classes_names_row: list):
    """Извлечение названий классов."""
    classes_names = []
    for cell in classes_names_row[1:]:
        if cell != "":
            classes_names.append(cell.split()[0].split("(")[0])
    return classes_names


async def _get_schedule_bells(schedule: list):
    """Получение расписания перемен."""
    schedule_bells = []
    for i in range(len(schedule)):
        schedule_bells.append(schedule[i][1])
        schedule[i] = schedule[i][2:]
    for i in range(len(schedule_bells)):
        true_bell = []
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
        schedule_bells[i] = "-".join([i for i in true_bell])

    return schedule_bells, schedule


async def _split_schedule_by_classes(classes_count: int, schedules: list):
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
                schedule = schedule[:index] + [schedule[index] for _ in range(classes_count - count)] + schedule[index:]
            if schedule[i] == "" or schedule[i] == "-" or schedule[i] == ".":
                schedule[i] = "нет урока"
            class_schedule.append(schedule[i])
        classes_schedules.append(class_schedule)

    return classes_schedules


async def _join_classes_schedule_with_bells(
    classes_schedules: list, bells: list, schedules: list
):
    """Объединение классов, звонков и расписания."""
    classes_schedules_with_bells = []
    for i in range(len(classes_schedules)):
        classes_schedules_with_bells.append([classes_schedules[i], schedules[i], bells])

    return classes_schedules_with_bells
