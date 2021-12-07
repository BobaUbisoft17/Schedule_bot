from PIL import Image, ImageDraw, ImageFont
from csv_parser import get_classes_schedules
import os 
import glob


PATH = "schedule_bot/schedule_image/"


async def del_img():
    """Функция для удаления старого расписания."""
    imgs = glob.glob(PATH + '*')
    for img in imgs:
        os.remove(img)

async def make_image(date):
    """Фунция для создания изображения с расписанием."""
    await del_img()
    list_10_11 = []
    date = await get_date(date)
    for class_ in await get_classes_schedules():
        class_name = class_.class_name
        list_schedule = class_.schedule
        bells = class_.bells

        if class_name in list_10_11:
            date = await get_next_date(date)
        else:
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
        background = ImageDraw.Draw(out)
        add_blocks = ImageDraw.Draw(out_2)
        add_blocks.multiline_text((430, 200), f"{date}\n{class_name}", font=font_to_heading, fill="grey", anchor="ms")
        out.paste(out_2, (0, 0))
        count_hight = 400
        if len(list_schedule) == 8:
            for i in range(8):
                lesson = Image.new("RGB", (1442, 125), "white")
                insert_for_item_name = ImageDraw.Draw(lesson)
                if list_schedule[i] == "нет урока" or list_schedule[i] == "":
                    insert_for_item_name.text((145, 15), list_schedule[i][:23], font=font_to_lessons, fill="grey")
                    insert_for_item_name.text((970, 30), bells[i], font=fnt, fill="grey")
                    insert_for_item_name.line([(150, 100), (1292, 100)], fill="grey", width=4)
                else:
                    insert_for_item_name.text((145, 15), list_schedule[i][:23], font=font_to_lessons, fill="black")
                    insert_for_item_name.text((970, 30), bells[i], font=fnt, fill="grey")
                    insert_for_item_name.line([(150, 100), (1292, 100)], fill="grey", width=4)
                out.paste(lesson, (0, count_hight))
                count_hight += 125
        else:
            for i in range(len(bells)):
                lesson = Image.new("RGB", (1442, 143), "white")
                insert_for_item_name = ImageDraw.Draw(lesson)
                if list_schedule[i] == "нет урока" or list_schedule[i] == "":
                    insert_for_item_name.text((145, 15), list_schedule[i][:23], font=font_to_lessons, fill="grey")
                    insert_for_item_name.text((970, 30), bells[i], font=fnt, fill="grey")
                    insert_for_item_name.line([(150, 100), (1292, 100)], fill="grey", width=4)
                else:
                    insert_for_item_name.text((145, 15), list_schedule[i][:23], font=font_to_lessons, fill="black")
                    insert_for_item_name.text((970, 30), bells[i], font=fnt, fill="grey")
                    insert_for_item_name.line([(150, 100), (1292, 100)], fill="grey", width=4)
                out.paste(lesson, (0, count_hight))
                count_hight += 143



        filename = f"{PATH}{class_name}.jpg"
        if filename in glob.glob(PATH):
            out.save(PATH + class_name + "_st.jpg")
        else:
            out.save(PATH + class_name + ".jpg")


async def get_date(date):
    """Функция для получения даты расписания."""
    if len(date[0].split(".")) == 2:
        day, month = date[0].split(".")
        year = ""
    else:
        day, month, year = date[0].split(".")
    return f"{day} {await get_month(int(month))} 20{year}"


async def get_next_date(date):
    """Функция для получения даты расписания + 1 день."""

    """В основном используется для получения даты расписания на субботу."""
    if len(date[0].split(".")) == 2:
        day, month = date[0].split(".")
        year = ""
    else:
        day, month, year = date[0].split(".")
    month_31 = [1, 3, 5, 7, 8, 10, 12]
    if month in month_31:
        if 1 <= int(day) + 1 < 31:
            return int(day) + 1, await get_month(int(month)), year
        else:
            if int(month) == 12:
                return 1, await get_month(1), int(year) + 1
            else:
                return 1, await get_month(int(month) + 1), year
    else:
        if 0 <= int(day) + 1 <= 30 and int(month) != 2:
            return int(day) + 1, await get_month(int(month)), year
        elif int(month) == 2:
            if (int("20" + year) % 4 == 0) or (int("20" + year) % 400 == 0 and int("20" + year) % 100 == 0):
                if int(day) < 29:
                    return int(day) + 1, await get_month(int(month)), year
                else:
                    return 1, await get_month(int(month) + 1), year
            else:
                if int(day) < 28:
                    return int(day) + 1, await get_month(int(month)), year
                else:
                    return 1, await get_month(int(month) + 1), year


async def get_month(number_of_month):
    """Функция преобразования числа месяца в название месяца."""
    month = {1 : "января",
             2 : "февраля",
             3 : "марта",
             4 : "апреля",
             5 : "мая",
             6 : "июня",
             7 : "июля",
             8 : "августа",
             9 : "сентября",
             10 : "октября",
             11 : "ноября",
             12 : "декабря"}
    return month[number_of_month]
