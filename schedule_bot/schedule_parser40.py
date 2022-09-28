"""Файл для парсинга расписания на сайте школы №40."""

import asyncio
import glob
import os
from typing import List, Tuple

import aiofiles
import aiohttp
import bs4
from vkbottle.bot import Bot

from convert_text_to_image import del_img, make_image, save_img
from mailing import mailing_list
from xls_parser import get_classes_schedules


URL = "https://s11028.edu35.ru/2013-06-12-15-17-31/raspisanie"
PATH = "schedule_tables/school40/"


async def check_for_innovation(filename: str) -> Tuple[bool, str]:
    """Функция для проверки актуальности расписания."""
    xls_files = glob.glob(PATH + "*.xls")
    if xls_files == []:
        return True, "New"
    else:
        xls_filenames = [os.path.split(file)[-1] for file in xls_files]
        if filename not in xls_filenames and len(xls_filenames) == 2:
            for file in xls_files:
                os.remove(file)
            return True, "New"
        elif filename not in xls_filenames and len(xls_filenames) == 1:
            return True, "New"
        else:
            return False, "No"


async def get_html(url: str) -> Tuple[str, int]:
    """Получение кода страницы."""
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            html_code = await response.text()
            return html_code, response.status


async def get_link_and_filename(html_code: str) -> List[Tuple[str, str]]:
    """Получение ссылки на файл и названия файла из HTML-кода страницы."""
    links_and_filenames = []
    class_schedule = ["even", "odd"]
    soup = bs4.BeautifulSoup(html_code, "lxml")
    for class_ in class_schedule:
        links_and_filenames.append(
            await get_schedule(soup.find_all("tr", class_=class_))
        )
    return links_and_filenames


async def get_schedule(list_schedules: bs4.element.ResultSet) -> Tuple[str, str]:
    """Получение ссылки на актуальное расписание."""
    schedules = []
    for schedule in list_schedules:
        schedules.append(schedule.find("a", class_="at_icon").get("href"))
    max_date = sorted(
        schedules, key=lambda x: int(x.split("/")[-1].split()[0]), reverse=True
    )[0]
    min_date = sorted(
        schedules, key=lambda x: int(x.split("/")[-1].split()[0])
    )[0]
    if min_date.split("/")[-1].split()[1] == "1" and (
        max_date.split("/")[-1].split()[1] == "30"
        or max_date.split("/")[-1].split()[1] == "31"
        or max_date.split("/")[-1].split()[1] == "28"
        or max_date.split("/")[-1].split()[1] == "27"
    ):
        max_date = min_date
    return max_date.split("/")[-1], max_date


async def get_date(filename: str) -> str:
    """Получение номера месяца по названию."""
    month = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }
    if "." not in filename[1]:
        return f"{filename[0]}.{month[filename[1]]}"
    else:
        return f"{filename[0]}.{month[filename[1].split('.')[0]]}"


async def get_files(schedules: List[Tuple[str, str]]) -> Tuple[bool, str, str]:
    """Сохранение файлов с расписанием."""
    for schedule in schedules:
        filename, link = schedule
        bool_meaning, status = await check_for_innovation(
                                    filename.split("/")[-1]
                                )
        if bool_meaning:
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(link) as response:
                    async with aiofiles.open(PATH + filename, "wb") \
                     as schedule:
                        await schedule.write(await response.content.read())
            date = await get_date(filename.lower().split()[:2])
        else:
            return False, "", status
    return True, date, status


async def parse40(bot: Bot) -> None:
    """Проверка ответа сервера, рендер изображений и рассылка."""
    while True:
        if glob.glob(PATH + "*.xls") == []:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)
        code, status_code = await get_html(URL)
        if status_code == 200:
            bool_meaning, date, status = await get_files(
                await get_link_and_filename(code)
            )
            if bool_meaning:
                schedules = get_classes_schedules()
                del_img("40")
                save_img(make_image(schedules, date.split()), "40")
                await mailing_list(bot, status, "40")
