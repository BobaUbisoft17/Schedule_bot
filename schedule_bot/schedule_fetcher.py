import asyncio
from typing import Tuple

import requests
from bs4 import BeautifulSoup

from convert_pdf_to_csv import convert_pdf_schedule_to_csv_tables
from convert_text_to_image import make_image
from repositories.schedule_repository import ScheduleRepository, ScheduleStatus
from repositories.subscriber_repository import SubscriberRepository


SCHEDULES_PAGE_URL = "https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "accept": "*/*",
}


async def get_link_and_filename(html: str) -> Tuple[str, str]:
    """Получение ссылки на файл и названия файла из HTML-кода страницы."""
    soup = BeautifulSoup(html, "lxml")
    schedules = soup.find_all("a", class_="at_url")
    schedules = [
        [
            schedule.get("href").split("/")[-1].split()[0].split()[0].split("."),
            schedule.get("href"),
        ]
        for schedule in schedules
    ]

    max_date = [["0", "0"], ""]
    for schedule in schedules:
        if (
            int(schedule[0][0]) > int(max_date[0][0])
            and int(schedule[0][1]) >= int(max_date[0][1])
        ) or (
            int(schedule[0][0]) < int(max_date[0][0])
            and int(schedule[0][1]) > int(max_date[0][1])
        ):
            max_date = schedule

    return max_date[1].split("/")[-1], max_date[1]


def download_schedules(filename: str, link: str):
    """Сохранение файла с расписанием."""
    response = requests.get(link, headers=HEADERS)
    ScheduleRepository().save(filename, response.content)
    convert_pdf_schedule_to_csv_tables(filename)  # ! неявный side effect


async def parse(bot):
    """Проверка ответа сервера и запись данных в бд."""
    while True:
        schedules_files = ScheduleRepository().get_all()
        if not schedules_files:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1800)

        response = requests.get(SCHEDULES_PAGE_URL, headers=HEADERS)
        if response.status_code != 200:
            continue

        schedule_url, schedule_filename = get_link_and_filename(
            response.content
        )
        schedule_status = ScheduleRepository().check_status(schedule_filename)
        if schedule_status == ScheduleStatus.SAME:
            continue

        download_schedules(schedule_url, schedule_filename)

        # дальше идёт код, который не должен здесь находится
        make_image(schedule_filename.split())
        if schedule_status == ScheduleStatus.UPDATE:
            message_text = "Появилось обновлённое расписание"
        elif schedule_status == ScheduleStatus.NEW:
            message_text = "Появилось новое расписание"

        for subscriber_id in SubscriberRepository().get_all():
            await bot.api_context.messages.send(
                peer_id=subscriber_id,
                message=message_text,
                random_id=0,
            )
