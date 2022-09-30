"""Файл для получения расписания из .pdf файлов."""

import glob
from typing import List, Tuple

from convert_text_to_image import Schedule

import pdfplumber


def get_classes_schedules() -> List[Schedule]:
    """Получение расписаний всех классов из .pdf файлов."""
    classes_schedules = []
    for file in _get_pdf_files():
        schedules = _fetch_classes_schedules_from_pdf(file)
        classes_schedules.extend(schedules)
    return classes_schedules


def _fetch_classes_schedules_from_pdf(filename: str) -> List[Schedule]:
    """Получение расписаний классов из .pdf файла."""
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
                        lesson = [
                            element
                            for element in table[row]
                            if element != "" and element is not None
                        ]
                    else:
                        lesson = [
                            element
                            for element in table[row]
                            if element is not None
                        ]
                    if len(lesson) > 1:
                        lessons.append(lesson)
                list_tables.append(lessons)
    for table in list_tables:
        classnames, *schedule = table
        schedule_bells, schedule = _get_schedule_bells(schedule)
        classes_schedules = _split_schedule_by_classes(
                                len(classnames),
                                schedule
                            )
        schedules.extend(
            _join_classes_schedule_with_bells(
                classnames, schedule_bells, classes_schedules
            )
        )

    return schedules


def _get_pdf_files() -> List[str]:
    """Полученеия .pdf файлов в текущей директории."""
    return glob.glob("schedule_tables/school14/*.pdf")


def _get_schedule_bells(schedule: List[List[str]]) -> Tuple[List[str], List[List[str]]]:
    """Получение расписания перемен."""
    schedule_bells = []
    timetable = []
    for lesson in schedule:
        if len(lesson[0]) > 1:
            schedule_bells.append(lesson[0])
            timetable.append(lesson[1:])
        else:
            schedule_bells.append(lesson[1])
            timetable.append(lesson[2:])
    for i in range(len(schedule_bells)):
        true_bell = []
        if "\n" not in schedule_bells[i]:
            separator = "-"
        else:
            separator = "-\n"
        for bell in schedule_bells[i].split(separator):
            true_bell_schedule = []
            bell = bell.replace(":", ".")
            for time in bell.split("."):
                if len(time) < 2 and time != "":
                    time = "0" + time
                elif time == "":
                    time = "не указано"
                true_bell_schedule.append(time)
            true_bell.append(".".join(list(true_bell_schedule)))
        schedule_bells[i] = "-".join(list(true_bell))
    return schedule_bells, timetable


def _split_schedule_by_classes(
    classes_count: int, schedules: List[List[str]]
) -> List[List[str]]:
    """Распределение расписания по классам."""
    classes_schedules = []
    for i in range(classes_count):
        class_schedule = []
        big_message = ""
        message_index = 0
        count_pass = 0
        for j in range(len(schedules)):
            schedule = schedules[j]
            if (("классный час" in schedule or "Классный час" in schedule) and \
                len(schedule) == 1) or len(schedule) == 1:
                schedule *= classes_count
            if schedule == []:
                schedule = [""] * classes_count
            elif len(schedule) < classes_count and len(schedule) != 1:
                if len(schedule) < classes_count and j != 0:
                    count = 0
                    while len(schedule) != classes_count:
                        if len(schedules[j - 1][count]) >= 25:
                            schedule = schedule[:count] + [schedules[j - 1][count]] + schedule[count:]
                        count += 1
                elif big_message == "":
                    count = 0
                    for lesson in schedule:
                        if len(lesson) >= 25:
                            big_message = lesson
                            index = schedule.index(lesson)
                        else:
                            count += 1
                    message_index = index
                    count_pass = count
                    schedule = (
                        schedule[:index]
                        + [
                            schedule[index].lower()
                            for _ in range(classes_count - count)
                        ]
                        + schedule[index + 1:]
                    )
                else:
                    schedule = (
                        schedule[:message_index]
                        + [
                            big_message.lower()
                            for _ in range(classes_count - count_pass)
                        ]
                        + schedule[message_index:]
                    )
            if schedule[i] == "" or schedule[i] == "-" or schedule[i] == ".":
                schedule[i] = "нет урока"
            class_schedule.append(schedule[i])
        classes_schedules.append(class_schedule)

    return classes_schedules


def _join_classes_schedule_with_bells(
    classnames: List[str], bells: List[str], schedules: List[List[str]]
) -> List[Schedule]:
    """Объединение классов, звонков и расписания."""
    schedule = []
    for i in range(len(classnames)):
        schedule.append(Schedule(classnames[i], schedules[i], bells))
    return schedule
