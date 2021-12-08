from typing import Optional, Tuple
import requests
from requests import Response
from bs4 import BeautifulSoup
from convert_pdf_to_csv import convert
from convert_text_to_image import make_image
from database_users import get_id
import asyncio
import glob
import os

URL = 'https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov'
HEADERS = {
	'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
	'accept' : '*/*',
}
PATH = "schedule_bot/schedule_tables/"


async def check_for_innovation(filename: str):
	csv_files = glob.glob(PATH + "*.pdf")
	if csv_files == []:
		return True, "New"
	else:
		for file in csv_files:
			if file.split("\\")[-1] != filename:
				if file.split("\\")[-1] in filename:
					os.remove(file)
					return True, "Update"
				else:
					os.remove(file)
					return True, "New"
			else:
				return False, "No"


async def get_html(url: str, params: Optional[dict] = None) -> Response:
	"""Получение кода страницы."""
	r = requests.get(url, headers=HEADERS, params=params)
	return r


async def get_link_and_filename(html_code: str) -> Tuple[str, str]:
	"""Получение ссылки на файл и названия файла из HTML-кода страницы."""
	soup = BeautifulSoup(html_code, 'lxml')
	schedules = soup.find_all('a', class_='at_url')[-1]
	return schedules.get('href').split("/")[-1], schedules.get('href')


async def get_file(filename_and_link: Tuple[str, str]):
	"""Сохранение файла с расписанием."""
	filename, link = (i for i in filename_and_link)
	bools, status = await check_for_innovation(filename)
	if bools:
		response = requests.get(link)
		with open(PATH + filename, "wb") as schedule:
			schedule.write(response.content)
		await convert(filename)
		return True, filename, status
	else:
		return False, False, status


async def parse(bot):
	"""Проверка ответа сервера и запись данных в бд."""
	while True:
		csv_files = glob.glob(PATH + "*.pdf")
		if csv_files == []:
			asyncio.sleep(1)
		else:
			await asyncio.sleep(1800)
		html = await get_html(URL)
		if html.status_code == 200:
			bools, filename, status = await get_file(await get_link_and_filename(html.text))
			if bools:
				await make_image(filename.split())
				if status == "Update":
					for peer_id in get_id():
						await bot.api_context.messages.send(peer_id=peer_id, message="Появилось обновлённое расписание", random_id=0)
				elif status == "New":
					for peer_id in get_id():
						await bot.api_context.messages.send(peer_id=peer_id, message="Появилось новое расписание", random_id=0)

