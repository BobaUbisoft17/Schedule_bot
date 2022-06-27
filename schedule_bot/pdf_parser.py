"""Файл для получения расписания из .pdf файлов"""

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
    """Получение расписаний всех классов из .pdf файлов."""
    classes_schedules = []
    for file in await _get_pdf_files():
        for table in await _fetch_classes_schedules_from_pdf(file):
            for class_ in table:
                classes_schedules.append(
                    ClassSchedule(
                        class_name=class_[0], schedule=class_[1], bells=class_[2]
                    )
                )
        return classes_schedules


async def _fetch_classes_schedules_from_pdf(filename: str) -> List[Tuple[str, str]]:
    """Получение расписаний классов из .pdf файла."""
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
                        lesson = [
                            element
                            for element in table[row]
                            if element != "" and element is not None
                        ]
                        if len(lesson) > 1:
                            lessons.append(lesson)
                    else:
                        lesson = [element for element in table[row] if element is not None]
                        if len(lesson) > 1:
                            lessons.append(lesson)
                list_tables.append(lessons)
    for table in list_tables:
        classnames, *schedule = table
        # classnames = await _fetch_classes_names(classnames)
        schedule_bells, schedule = await _get_schedule_bells(schedule)
        classes_schedules = await _split_schedule_by_classes(len(classnames), schedule)
        schedules.append(
            await _join_classes_schedule_with_bells(
                classnames, schedule_bells, classes_schedules
            )
        )

    return schedules


async def _get_pdf_files() -> List[str]:
    """Полученеия .pdf файлов в текущей директории."""
    return glob.glob("schedule_tables/school14/*.pdf")


async def _fetch_classes_names(classes_names_row: list) -> List[str]:
    """Извлечение названий классов."""
    classes_names = []
    for cell in classes_names_row[1:]:
        if cell != "":
            classes_names.append(cell.split()[0].split("(")[0])
    return classes_names


async def _get_schedule_bells(schedule: List) -> Tuple[List, List]:
    """Получение расписания перемен."""
    schedule_bells = []
    timetable = []
    for lesson in schedule:
        if len(lesson[0]) == 1:
            schedule_bells.append(lesson[1])
            timetable.append(lesson[2:])
        else:
            schedule_bells.append(lesson[0])
            timetable.append(lesson[1:])
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


async def _split_schedule_by_classes(classes_count: int, schedules: list) -> List[List]:
    """Распределение расписания по классам."""
    classes_schedules = []
    for i in range(classes_count):
        class_schedule = []
        big_message = ""
        message_index = 0
        count_pass = 0
        for schedule in schedules:
            if ("классный час" in schedule or "Классный час" in schedule) and len(
                schedule
            ) == 1:
                schedule *= len(classes_count)
            if len(schedule) < classes_count and len(schedule) != 1:
                if big_message == "":
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


async def _join_classes_schedule_with_bells(
    classnames: list, bells: list, schedules: list
) -> List[List]:
    """Объединение классов, звонков и расписания."""
    schedule = []
    for i in range(len(classnames)):
        schedule.append([classnames[i], schedules[i], bells])
    return schedule
