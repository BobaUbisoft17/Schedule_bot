from dataclasses import dataclass

import os
import csv
import glob


PATH = "csv_schedule/*.csv"


@dataclass
class Schedule:
    class_name: str
    schedule_and_bells: str


def get_csv_files(path):
    csv_files = glob.glob(path)
    return csv_files


def get_tables(file):
    with open(file, encoding="utf-8") as table:
        table_reader = csv.reader(table, delimiter=";")
        list_schedules = list(table_reader)
        schedule_bell = []
        full_schedule = []
        fully_schedule = []
        classes = []
        classes.extend([i for i in list_schedules[0] if 2 <= len(i) <= 3])
        list_schedules = list_schedules[1:]
        for i in range(len(list_schedules)):
            schedule_bell.append(list_schedules[i][1])
            list_schedules[i] = list_schedules[i][2:]
        for clas in range(len(classes)):
            lite_schedule = []
            for schedule in list_schedules:
                if schedule[clas] == "" or schedule[clas] == "-":
                    schedule[clas] = "окно"
                lite_schedule.append(schedule[clas])
            full_schedule.append(lite_schedule)
        for full in full_schedule:
            string_schedule = ""
            for i, j in zip(schedule_bell, full):
                string_schedule += f"{i} {j}\n"
            fully_schedule.append(string_schedule)
        schedule_with_classes = []
        for clas, schedule in zip(classes, fully_schedule):
            schedules = []
            schedules.append(clas)
            schedules.append(schedule)
            schedule_with_classes.append(schedules)
        return schedule_with_classes


def give_to_class():
    schedule = []
    for file in get_csv_files(PATH):
        for i in get_tables(file):
            schedule.append(
                Schedule(
                    class_name=i[0],
                    schedule_and_bells=i[-1],
                )
            )
        os.remove(file)
    return schedule
