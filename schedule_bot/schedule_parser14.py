"""Файл для парсинга расписания на сайте школы №14."""

import asyncio
import datetime
import glob
import os
from typing import List, Tuple

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from convert_text_to_image import collect_images, del_img, save_img
from logger import logger
from mailing import mailing_list
from pdf_parser import get_classes_schedules
from utils import get_date
from vkbottle.bot import Bot


URL = "https://s11018.edu35.ru/"
PATH = "schedule_tables/school14/"


async def check_for_innovation(filename: str) -> Tuple[bool, str]:
    """Функция для проверки актуальности расписания."""
    if glob.glob(PATH + "*.pdf") == []:
        return True, "New"
    pdf_files = [os.path.split(file)[-1] for file in glob.glob(PATH + "*.pdf")]
    for file in pdf_files:
        if file != filename:
            os.remove(PATH + file)
            if file.split()[0] in filename:
                return True, "Update"
            return True, "New"
    return False, "No"


async def get_html(url: str) -> Tuple[str, int]:
    """Получение кода страницы."""
    connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            html_code = await response.text()
            return html_code, response.status


def get_link_tag_names(html_code: str) -> List[str]:
    """Получение тегов с ссылками на фалы с расписанием."""
    soup = BeautifulSoup(html_code, "lxml")
    html_schedules = soup.find_all(
        "span", style="font-family: 'book antiqua', palatino; font-size: 14pt;"
    )
    if soup.find_all("a", class_="at_url") == []:
        schedules = []
        for schedule in html_schedules:
            schedules.extend(schedule.find_all("a"))
        return schedules
    return soup.find_all("a", class_="at_url")


def get_file_links(link_tags: str) -> List[str]:
    """Получение ссылок из тегов."""
    date_and_links = []
    for tag in link_tags:
        link = tag.get("href")
        if "doc" in link:
            link = URL + link
        date_and_links.append(
            [
                get_date(link.split("/")[-1]),
                link
            ]
        )
    return date_and_links


def get_max_date(links_and_filenames: List[List[str]]) -> str:
    """Сортировка ссылок по дате."""
    return sorted(
        links_and_filenames,
        key=lambda x: datetime.datetime.strptime(
            x[0],
            "%d.%m.%y"
        ),
        reverse=True
    )[0]


async def get_link_and_filename(html_code: str) -> Tuple[str, str]:
    """Получение ссылки на файл и названия файла из HTML-кода страницы."""
    tags = get_link_tag_names(html_code)
    links = get_file_links(tags)
    max_date_schedule = get_max_date(links)
    filename = max_date_schedule[1].split("/")[-1]
    link = max_date_schedule[1]
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


async def update_schedule(bot: Bot, html_code: str) -> None:
    """Обновление расписания и оповещение пользователей."""
    bool_meaning, filename, status = await get_file(
        await get_link_and_filename(html_code)
    )
    if bool_meaning:
        schedules = get_classes_schedules()
        schedule_name = get_date(filename)
        save_img(
            collect_images(
                schedules, schedule_name.split()
            ),
            "14"
        )
        await mailing_list(bot, status, "14")


@logger.catch
async def parse14(bot: Bot) -> None:
    """Проверка ответа сервера и запись данных в бд."""
    while True:
        timer = 1800
        pdf_files = glob.glob(PATH + "*.pdf")
        if pdf_files == []:
            timer = 1
        await asyncio.sleep(timer)
        html, status = (
            await get_html(URL + "obuchayushchimsya/raspisanie-urokov/")
        )
        if status == 200:
            await update_schedule(bot, html)
