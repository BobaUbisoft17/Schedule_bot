from typing import Optional, Tuple
from bs4 import BeautifulSoup
from convert_pdf_to_csv import convert
from convert_text_to_image import make_image
from db_users import get_users_id
from database_users import get_id, del_id
from vkbottle import CodeException
import asyncio
import glob
import os
import aiohttp
import aiofiles

URL = "https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "*/*",
}
PATH = "schedule_tables/school14/"


async def check_for_innovation(filename: str):
    csv_files = glob.glob(PATH + "*.pdf")
    if csv_files == []:
        return True, "New"
    else:
        for file in csv_files:
            if os.path.split(file)[-1] != filename:
                if (os.path.split(file)[-1]).split()[0] in filename:
                    os.remove(file)
                    return True, "Update"
                else:
                    os.remove(file)
                    return True, "New"
            else:
                return False, "No"


async def get_html(url: str, params: Optional[dict] = None):
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
            schedule.get("href").split("/")[-1].split()[0].split()[0].split("."),
            schedule.get("href"),
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


async def get_file(filename_and_link: Tuple[str, str]):
    """Сохранение файла с расписанием."""
    filename, link = (i for i in filename_and_link)
    bools, status = await check_for_innovation(filename)
    if bools:
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(link) as response:
                async with aiofiles.open(PATH + filename, "wb") as schedule:
                    await schedule.write(await response.content.read())
        return True, filename, status
    else:
        return False, False, status


async def parse(bot):
    """Проверка ответа сервера и запись данных в бд."""
    while True:
        csv_files = glob.glob(PATH + "*.pdf")
        if csv_files == []:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1800)
        html, status = await get_html(URL)
        if status == 200:
            bools, filename, status = await get_file(await get_link_and_filename(html))
            if bools:
                await make_image(filename.split(), "14")
                if status == "Update":
                    for user_id in await get_users_id("14"):
                        try:
                            await bot.api.messages.send(
                                user_id=user_id,
                                message="Появилось обновлённое расписание",
                                random_id=0,
                            )
                        except CodeException:
                            print(user_id)
                elif status == "New":
                    for user_id in await get_id():
                        try:
                            await bot.api.messages.send(
                                user_id=user_id,
                                message="Появилось новое расписание",
                                random_id=0,
                            )
                        except CodeException:
                            await del_id(user_id)
