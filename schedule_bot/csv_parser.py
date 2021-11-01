from dataclasses import dataclass

import os
import csv
import glob
from typing import List, Tuple


PATH = "*.csv"


@dataclass
class Schedule:
    clas: str
    schedule: str


def get_csv_files(path: list) -> List[str]:
    """Функция для полученеия всех .csv файлов, возвращает список .csv файлов"""
    csv_files = glob.glob(path)
    return csv_files


def get_tables(file: str) -> List[Tuple[str, str]]:
    """Функция для чтения информации из .csv файлов"""
    with open(file, encoding="utf-8") as table:
        table_reader = csv.reader(table, delimiter=";")
        list_schedules = list(table_reader)
        classes_names, *list_schedules = list_schedules
        classes_names = get_classes(classes_names)
        schedule_bell, list_schedules = get_schedule_bell(list_schedules)
        schedule = get_schedule(len(classes_names), list_schedules)
        return clas_schedule_bell_consolidation(classes_names, schedule_bell, schedule)


def get_classes(list_of_classes: list):
    """Функция для извлечения названия классов."""
    return [clas.replace(' ', '') for clas in list_of_classes if '(' in clas or ')' in clas]


def get_schedule_bell(list_schedules: list):
    """Функция для получения расписания звонков."""
    schedule_bell = []
    for i in range(len(list_schedules)):
        schedule_bell.append(list_schedules[i][1])
        list_schedules[i] = list_schedules[i][2:]
    return schedule_bell, list_schedules


def get_schedule(number_of_classes: int, schedules: list):
    """Функция для рапспределения расписания по классам"""
    schedule_for_all_classes = []
    for number in range(number_of_classes):
        schedule_for_one_clas = []
        for schedule in schedules:
            if ("классный час" in schedule or "Классный час" in schedule) and len(schedule) == 1:
                schedule *= number
            if schedule[number] == "" or schedule[number] == "-":
                schedule[number] = "окно"
            schedule_for_one_clas.append(schedule[number])
        schedule_for_all_classes.append(schedule_for_one_clas)
    return schedule_for_all_classes


def clas_schedule_bell_consolidation(classes: list, bells: list, schedules: list):
    """Функция для объединения классов, звонков и расписания"""
    list_of_schedules = []
    for clas in range(len(classes)):
        full_schedule = classes[clas] + '\n'
        for bell, schedule in zip(bells, schedules[clas]):
            full_schedule += f"{bell} {schedule}\n"
        list_of_schedules.append([classes[clas], full_schedule])
    return list_of_schedules
    

def give_to_class() -> List[Schedule]:
    """Функция для переноса информации из .csv файла в дата класс"""
    schedule = []
    for file in get_csv_files(PATH):
        for table in get_tables(file):
            schedule.append(
                Schedule(
                    clas=table[0],
                    schedule=table[-1],
                )
            )
        os.remove(file)
    return schedule
