from dataclasses import dataclass
from typing import List, Tuple
import pdfplumber
import glob


@dataclass
class ClassSchedule:
    class_name: str
    schedule: list
    bells: list


async def get_classes_schedules() -> List[ClassSchedule]:
    classes_schedules = []
    for file in await _get_pdf_files():
        for table in await _fetch_classes_schedules_from_pdf(file):
            for class_ in table:
                classes_schedules.append(
                    ClassSchedule(class_name=class_[0], schedule=class_[1], bells=class_[2])
                )
        return classes_schedules


async def _fetch_classes_schedules_from_pdf(filename):
    tables = []
    schedules = []
    with pdfplumber.open(filename) as pdf:
        list_tables = []
        pages = pdf.pages
        for page in pages:
            tables = page.extract_tables()
            for table in tables:
                lessons = []
                for row in range(len(table)):
                    if row == 0:
                        lessons.append([element for element in table[row] if element != "" and element != None])
                    else:
                        lessons.append([element for element in table[row] if element != None])
                list_tables.append(lessons)
    for table in list_tables:
        classnames, *schedule = table
        schedule_bells, schedule = await _get_schedule_bells(schedule)
        classes_schedules = await _split_schedule_by_classes(len(classnames), schedule)
        schedules.append(await _join_classes_schedule_with_bells(
        classnames, schedule_bells, classes_schedules
    ))

    return schedules


async def _get_pdf_files() -> List[str]:
    return glob.glob("schedule_tables/school14/*.pdf")


async def _get_schedule_bells(schedule):
    schedule_bells = []
    timetable = []
    for lesson in schedule:
        schedule_bells.append(lesson[1])
        timetable.append(lesson[2:])
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
    return schedule_bells, timetable
    

async def _split_schedule_by_classes(classes_count: int, schedules: list):
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
                    if len(lesson) >= 25:
                        index = schedule.index(lesson)
                        break
                schedule = schedule[:index] + [schedule[index] for _ in range(classes_count - count)] + schedule[index:]
            if schedule[i] == "" or schedule[i] == "-" or schedule[i] == ".":
                schedule[i] = "нет урока"
            class_schedule.append(schedule[i])
        classes_schedules.append(class_schedule)

    return classes_schedules


async def _join_classes_schedule_with_bells(classnames: list, bells: list, schedules: list):
    schedule = []
    for i in range(len(classnames)):
        schedule.append([classnames[i], schedules[i], bells])
    return schedule
