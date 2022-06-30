"""Файл для создания изображений с расписанием."""

import datetime
from typing import List
from PIL import Image, ImageDraw, ImageFont
import pdf_parser
import xls_parser
import os
import glob


PATH = "schedule_image/"


async def del_img(school: str) -> None:
    """Функция для удаления старого расписания."""
    imgs = glob.glob(PATH + "school" + school + "/*")
    for img in imgs:
        os.remove(img)


async def get_schedules(school: str) -> List:
    if school == "14":
        return await pdf_parser.get_classes_schedules()
    elif school == "40":
        return await xls_parser.get_classes_schedules()


async def make_image(date: List, school: str) -> None:
    """Фунция для создания изображения с расписанием."""
    await del_img(school)
    day, month = map(int, date[0].split(".")[:2])
    year = int(datetime.datetime.now().strftime("%Y"))
    date = datetime.date(year=year, month=month, day=day)
    list_10_11 = []
    date_first_number = await get_date(date)
    next_date = await get_next_date(date)
    for class_ in await get_schedules(school):
        class_name = class_.class_name
        list_schedule = class_.schedule
        bells = class_.bells

        if class_name in list_10_11:
            date = next_date
        else:
            date = date_first_number
            list_10_11.append(class_name)
        # create an image
        out = Image.new("RGB", (1442, 1600), "white")
        if len(list_schedule) < len(bells):
            list_schedule += ["нет урока"] * (len(bells) - len(list_schedule))

        # get a font
        font_to_heading = ImageFont.truetype("arial.ttf", 80)
        fnt = ImageFont.truetype("arial.ttf", 60)
        font_to_lessons = ImageFont.truetype("arial.ttf", 70)
        # get a drawing context
        out_2 = Image.new("RGB", (1442, 400), "white")
        add_blocks = ImageDraw.Draw(out_2)
        add_blocks.multiline_text(
            (140, 125),
            f"{date}\n{class_name}",
            font=font_to_heading,
            fill="grey",
            spacing=25,
        )
        out.paste(out_2, (0, 0))
        count_hight = 400
        if len(list_schedule) > 7:
            pix_for_one_lesson = 1100 // len(list_schedule)
            for i in range(len(list_schedule)):
                lesson = Image.new("RGB", (1442, pix_for_one_lesson), "white")
                insert_for_item_name = ImageDraw.Draw(lesson)
                if (
                    list_schedule[i] == "нет урока"
                    or list_schedule[i] == ""
                    or list_schedule[i] == "нет урока "
                ):
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:20],
                        font=font_to_lessons,
                        fill="grey",
                    )
                    insert_for_item_name.text(
                        (970, 30), bells[i], font=fnt, fill="grey"
                    )
                    insert_for_item_name.line(
                        [(150, 100), (1292, 100)], fill="grey", width=4
                    )
                else:
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:20],
                        font=font_to_lessons,
                        fill="black",
                    )
                    insert_for_item_name.text(
                        (970, 30), bells[i], font=fnt, fill="grey"
                    )
                    insert_for_item_name.line(
                        [(150, 100), (1292, 100)], fill="grey", width=4
                    )
                out.paste(lesson, (0, count_hight))
                count_hight += pix_for_one_lesson
        else:
            for i in range(len(bells)):
                lesson = Image.new("RGB", (1442, 143), "white")
                insert_for_item_name = ImageDraw.Draw(lesson)
                if (
                    list_schedule[i] == "нет урока"
                    or list_schedule[i] == ""
                    or list_schedule[i] == "нет урока "
                ):
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:20],
                        font=font_to_lessons,
                        fill="grey",
                    )
                    insert_for_item_name.text(
                        (970, 30), bells[i], font=fnt, fill="grey"
                    )
                    insert_for_item_name.line(
                        [(150, 100), (1292, 100)], fill="grey", width=4
                    )
                else:
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:20],
                        font=font_to_lessons,
                        fill="black",
                    )
                    insert_for_item_name.text(
                        (970, 30), bells[i], font=fnt, fill="grey"
                    )
                    insert_for_item_name.line(
                        [(150, 100), (1292, 100)], fill="grey", width=4
                    )
                out.paste(lesson, (0, count_hight))
                count_hight += 143

        filename = f"{class_name}.jpg"
        schedules = [
            os.path.split(path)[-1]
            for path in glob.glob(PATH + "school" + school + "/*.jpg")
        ]
        if filename in schedules:
            out.save(os.path.join(PATH + "school" + school + "/", class_name + "2.jpg"))
        else:
            out.save(os.path.join(PATH + "school" + school + "/", class_name + ".jpg"))


async def get_date(date: datetime.date) -> str:
    """Функция для получения даты расписания."""
    return f"{date.strftime('%d.%m.%Y')} - {await get_week_day(date)}"


async def get_next_date(date: datetime.date) -> str:
    """Функция для получения даты расписания + 1 день."""

    """В основном используется для получения даты расписания на субботу."""
    next_day = date + datetime.timedelta(days=1)
    return f"{next_day.strftime('%d.%m.%Y')} - {await get_week_day(next_day)}"


async def get_week_day(date: datetime.date) -> str:
    days_of_week = {
        "Sunday": "воскресенье",
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
    }
    return days_of_week[date.strftime("%A")]
