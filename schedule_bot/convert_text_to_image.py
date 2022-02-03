import datetime
from types import ModuleType
from PIL import Image, ImageDraw, ImageFont
from csv_parser import get_classes_schedules
import os
import glob


PATH = "schedule_image/"


async def del_img():
    """Функция для удаления старого расписания."""
    imgs = glob.glob(PATH + "*")
    for img in imgs:
        os.remove(img)


async def make_image(date):
    """Фунция для создания изображения с расписанием."""
    await del_img()
    list_10_11 = []
    date_first_number = await get_date(date)
    next_date = await get_next_date(date)
    for class_ in await get_classes_schedules():
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
                if list_schedule[i] == "нет урока" or list_schedule[i] == "":
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:23],
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
                        list_schedule[i][:23],
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
                if list_schedule[i] == "нет урока" or list_schedule[i] == "":
                    insert_for_item_name.text(
                        (145, 15),
                        list_schedule[i][:23],
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
                        list_schedule[i][:23],
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
        schedules = [os.path.split(path)[-1] for path in glob.glob(PATH + "*.jpg")]
        if filename in schedules:
            out.save(os.path.join(PATH, class_name + "2.jpg"))
        else:
            out.save(os.path.join(PATH, class_name + ".jpg"))


async def get_date(date):
    """Функция для получения даты расписания."""
    if len(date[0].split(".")) == 2:
        day, month = date[0].split(".")
        if len(day) < 2:
            day = "0" + day
        if len(month) < 2:
            month = "0" + month
        year = datetime.datetime.now().strftime("%Y")
        return f"{day}.{month}.{year} - {await get_week_day(day, month, year)}"
    else:
        day, month, year = date[0].split(".")
        if len(day) < 2:
            day = "0" + day
        if len(month) < 2:
            month = "0" + month
        year = datetime.datetime.now().strftime("%Y")
        return f"{day}.{month}.{year} - {await get_week_day(day, month, year)}"


async def get_next_date(date):
    """Функция для получения даты расписания + 1 день."""

    """В основном используется для получения даты расписания на субботу."""
    if len(date[0].split(".")) == 2:
        day, month = date[0].split(".")
        year = datetime.datetime.now().strftime("%Y")
    else:
        day, month, year = date[0].split(".")
    if len(day) < 2:
        day = "0" + day
    if len(month) < 2:
        month = "0" + month
    year = datetime.datetime.now().strftime("%Y")
    day, month, year = (
        (
            datetime.date(int(year), int(month), int(day)) + datetime.timedelta(days=1)
        ).strftime("%d.%m.%Y")
    ).split(".")
    return f"{day}.{month}.{year} - {await get_week_day(day, month, year)}"


async def get_week_day(day, month, year):
    days_of_week = {
        "Sunday": "воскресенье",
        "Monday": "понедельник",
        "Tuesday": "вторник",
        "Wednesday": "среда",
        "Thursday": "четверг",
        "Friday": "пятница",
        "Saturday": "суббота",
    }
    return days_of_week[datetime.date(int(year), int(month), int(day)).strftime("%A")]
