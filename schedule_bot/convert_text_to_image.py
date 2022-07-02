"""Файл для создания изображений с расписанием."""

import datetime
from typing import List
from PIL import Image, ImageDraw, ImageFont
import os
import glob


PATH = "schedule_image/"


async def del_img(school: str) -> None:
    """Функция для удаления старого расписания."""
    imgs = glob.glob(PATH + "school" + school + "/*")
    for img in imgs:
        os.remove(img)


async def make_image(schedules: List, date: List) -> List:
    """Фунция для создания изображения с расписанием."""
    images_and_classes = []
    day, month = map(int, date[0].split(".")[:2])
    year = int(datetime.datetime.now().strftime("%Y"))
    date = datetime.date(year=year, month=month, day=day)
    list_10_11 = []
    date_first_number = await get_date(date)
    next_date = await get_next_date(date)
    for class_ in schedules:
        class_name = class_.class_name
        list_schedule = class_.schedule
        bells = class_.bells

        if class_name in list_10_11:
            date = next_date
        else:
            date = date_first_number
            list_10_11.append(class_name)
        # create an image
        img = Image.new("RGB", (1442, 1600), "white")
        if len(list_schedule) < len(bells):
            list_schedule += ["нет урока"] * (len(bells) - len(list_schedule))

        # get a font
        font_to_heading = ImageFont.truetype("arial.ttf", 80)
        font_to_bells = ImageFont.truetype("arial.ttf", 60)
        font_to_lessons = ImageFont.truetype("arial.ttf", 70)
        # get a drawing context
        block_with_date_and_classname = Image.new("RGB", (1442, 400), "white")
        add_block = ImageDraw.Draw(block_with_date_and_classname)
        add_block.multiline_text(
            (140, 125),
            f"{date}\n{class_name}",
            font=font_to_heading,
            fill="grey",
            spacing=25,
        )
        img.paste(block_with_date_and_classname, (0, 0))
        count_hight = 400
        if len(list_schedule) > 7:
            hight_for_one_block = 1100 // len(list_schedule)
        else:
            hight_for_one_block = 143
        for i in range(len(list_schedule)):
            block_with_lesson_and_bell = Image.new(
                mode="RGB", 
                size=(1442, hight_for_one_block), 
                color="white"
            )
            insert_in_block_with_lesson_and_bell = ImageDraw.Draw(block_with_lesson_and_bell)
            if list_schedule[i] in ("нет урока", "нет урока ", ""):
                fill = "grey"
            else:
                fill = "black"
            insert_in_block_with_lesson_and_bell.text(
                (145, 15),
                list_schedule[i][:20],
                font=font_to_lessons,
                fill=fill,
            )
            insert_in_block_with_lesson_and_bell.text(
                (970, 30), bells[i], font=font_to_bells, fill="grey"
            )
            insert_in_block_with_lesson_and_bell.line(
                [(150, 100), (1292, 100)], fill="grey", width=4
            )
            img.paste(block_with_lesson_and_bell, (0, count_hight))
            count_hight += hight_for_one_block
        images_and_classes.append([img, class_name])
    return images_and_classes


async def save_img(images_and_classes: List, school: str):
    for element in images_and_classes:
        img, class_name = element
        filename = f"{class_name}.jpg"
        schedules = [
            os.path.split(path)[-1]
            for path in glob.glob(PATH + "school" + school + "/*.jpg")
        ]
        
        if filename in schedules:
            img.save(os.path.join(PATH + "school" + school + "/", class_name + "2.jpg"))
        else:
            img.save(os.path.join(PATH + "school" + school + "/", class_name + ".jpg"))


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
