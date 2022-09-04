"""Файл для парсинга расписания на сайте школы №14."""

import asyncio
import glob
import os
from typing import Optional, Tuple

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from vkbottle.bot import Bot

from convert_text_to_image import del_img, make_image, save_img
from mailing import mailing_list
from pdf_parser import get_classes_schedules


URL = "https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov"
PATH = "schedule_tables/school14/"


async def check_for_innovation(filename: str) -> Tuple[bool, str]:
    """Функция для проверки актуальности расписания."""
    csv_files = glob.glob(PATH + "*.pdf")
    if csv_files == []:
        return True, "New"
    else:
        for file in csv_files:
            if os.path.split(file)[-1] != filename:
                if (os.path.split(file)[-1]).split()[1] in filename:
                    os.remove(file)
                    return True, "Update"
                else:
                    os.remove(file)
                    return True, "New"
    return False, "No"


async def get_html(url: str) -> Tuple[str, int]:
    """Получение кода страницы."""
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            html_code = await response.text()
            return html_code, response.status


async def get_link_and_filename(html_code: str) -> Tuple[str, str]:
    """Получение ссылки на файл и названия файла из HTML-кода страницы."""
    soup = BeautifulSoup(html_code, "lxml")
    schedules = soup.find_all("a", class_="at_url")
    schedules = [
        [
            schedule.get("href").split("/")[-1].split()[1].split()[0].split("."),
            schedule.get("href")
        ]
        for schedule in schedules
    ]
    max_date = [["0", "0"], ""]
    for i in range(len(schedules)):
        if (
            int(schedules[i][0][0]) > int(max_date[0][0])
            and int(schedules[i][0][1]) >= int(max_date[0][1])
        ) or (
            int(schedules[i][0][0]) < int(max_date[0][0])
            and int(schedules[i][0][1]) > int(max_date[0][1])
        ):
            max_date = schedules[i]
    filename = max_date[1].split("/")[-1]
    link = max_date[1]
    return filename, link


async def get_file(
    filename_and_link: Tuple[str, str]
) -> Tuple[bool, str, str]:
    """Сохранение файла с расписанием."""
    filename, link = (i for i in filename_and_link)
    bool_meaning, status = await check_for_innovation(filename)
    if bool_meaning:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(link) as response:
                async with aiofiles.open(PATH + filename, "wb") as schedule:
                    await schedule.write(await response.content.read())
        return True, filename, status
    else:
        return False, "", status


async def parse14(bot: Bot) -> None:
    """Проверка ответа сервера и запись данных в бд."""
    while True:
        csv_files = glob.glob(PATH + "*.pdf")
        if csv_files == []:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1800)
        html, status = await get_html(URL)
        if status == 200:
            bool_meaning, filename, status = await get_file(
                await get_link_and_filename(html)
            )
            if bool_meaning:
                schedules = get_classes_schedules()
                del_img("14")
                schedule_name = filename.split()
                schedule_name[0], schedule_name[1] = schedule_name[1], schedule_name[0]
                save_img(make_image(schedules, schedule_name), "14")
                await mailing_list(bot, status, "14")
