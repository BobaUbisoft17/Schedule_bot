"""Файл для парсинга расписания на сайте школы №40"""

import asyncio
from typing import List, Tuple
import aiohttp
from bs4 import BeautifulSoup
import aiofiles
import glob
import os
from vkbottle import CodeException
from db_users import get_users_id, unsubscribe_on_newsletter
from convert_text_to_image import make_image


URL = "https://s11028.edu35.ru/2013-06-12-15-17-31/raspisanie"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.81 Safari/537.36",
    "accept": "*/*",
}
PATH = "schedule_tables/school40/"


async def check_for_innovation(filename: str) -> tuple([bool, str]):
    xls_files = glob.glob(PATH + "*.xls")
    if xls_files == []:
        return True, "New"
    else:
        if filename not in xls_files and len(xls_files) == 2:
            for file in xls_files:
                os.remove(file)
            return True, "New"
        elif filename not in xls_files and len(xls_files) == 1:
            return True, "New"
        else:
            return False, "No"


async def get_html(url: str) -> tuple([str, int]):
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            html_code = await response.text()
            return html_code, response.status


async def get_link_and_filename(html_code: str) -> tuple([str, str]):
    soup = BeautifulSoup(html_code, "lxml")
    schedule_even = await get_even_schedule(soup.find_all("tr", class_="even"))
    schedule_odd = await get_odd_schedule(soup.find_all("tr", class_="odd"))
    return schedule_even, schedule_odd


async def get_even_schedule(list_schedules: List) -> tuple([str, str]):
    schedules = []
    for schedule in list_schedules:
        schedules.append(schedule.find("a", class_="at_icon").get("href"))
    max_date = sorted(
        schedules, key=lambda x: int(x.split("/")[-1].split()[0]), reverse=True
    )[0]
    min_date = sorted(schedules, key=lambda x: int(x.split("/")[-1].split()[0]))[0]
    if min_date.split("/")[-1].split()[1] == "1" and (
        max_date.split("/")[-1].split()[1] == "30"
        or max_date.split("/")[-1].split()[1] == "31"
        or max_date.split("/")[-1].split()[1] == "28"
        or max_date.split("/")[-1].split()[1] == "27"
    ):
        max_date = min_date
    return max_date.split("/")[-1], max_date


async def get_odd_schedule(list_schedules: List) -> tuple([str, str]):
    schedules = []
    for schedule in list_schedules:
        schedules.append(schedule.find("a", class_="at_icon").get("href"))
    max_date = sorted(
        schedules, key=lambda x: int(x.split("/")[-1].split()[0]), reverse=True
    )[0]
    min_date = sorted(schedules, key=lambda x: int(x.split("/")[-1].split()[0]))[0]
    if min_date.split("/")[-1].split()[1] == "1" and (
        max_date.split("/")[-1].split()[1] == "30"
        or max_date.split("/")[-1].split()[1] == "31"
        or max_date.split("/")[-1].split()[1] == "28"
        or max_date.split("/")[-1].split()[1] == "27"
    ):
        max_date = min_date
    return max_date.split("/")[-1], max_date


async def get_date(filename: str) -> str:
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
    return f"{filename[0]}.{month[filename[1]]} "


async def get_files(schedules: Tuple) -> tuple([bool, str, str]):
    for schedule in schedules:
        filename, link = schedule
        bool_meaning, status = await check_for_innovation(filename.split("/")[-1])
        if bool_meaning:
            connector = aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(link) as response:
                    async with aiofiles.open(PATH + filename, "wb") as schedule:
                        await schedule.write(await response.content.read())
            date = await get_date(filename.lower().split()[:2])
        else:
            return False, "", status
    return True, date, status


async def parse40(bot) -> None:
    while True:
        if glob.glob(PATH + "*.xls") == []:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1800)
        code, status_code = await get_html(URL)
        if status_code == 200:
            bool_meaning, date, status = await get_files(
                await get_link_and_filename(code)
            )
            if bool_meaning:
                await make_image(date.split(), "40")
                if status == "Update":
                    for user_id in await get_users_id("40"):
                        try:
                            await bot.api.messages.send(
                                user_id=user_id,
                                message="Появилось обновлённое расписание",
                                random_id=0,
                            )
                        except CodeException:
                            await unsubscribe_on_newsletter(user_id)
                elif status == "New":
                    for user_id in await get_users_id("40"):
                        try:
                            await bot.api.messages.send(
                                user_id=user_id,
                                message="Появилось новое расписание",
                                random_id=0,
                            )
                        except CodeException:
                            await unsubscribe_on_newsletter(user_id)
