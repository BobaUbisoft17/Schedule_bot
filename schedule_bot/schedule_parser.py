from typing import Optional, Tuple
import requests
from requests import Response
from bs4 import BeautifulSoup
from convert_pdf_to_csv import convert
from schedule_SQL import init_db
import glob
import os

URL = 'https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov'
HEADERS = {
	'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
	'accept' : '*/*',
}
PATH = "schedule_bot/"


def check_for_innovation(filename: str):
	csv_files = glob.glob("*.pdf")
	if csv_files == []:
		return True
	else:
		for file in csv_files:
			if file != filename:
				os.remove(file)
				return True
			else:
				return False


def get_html(url: str, params: Optional[dict] = None) -> Response:
	"""Получение кода страницы."""
	r = requests.get(url, headers=HEADERS, params=params)
	return r


def get_link_and_filename(html_code: str) -> Tuple[str, str]:
	"""Получение ссылки на файл и названия файла из HTML-кода страницы."""
	soup = BeautifulSoup(html_code, 'lxml')
	schedules = soup.find_all('a', class_='at_url')[-1]
	return schedules.get('href').split("/")[-1], schedules.get('href')


def get_file(filename_and_link: Tuple[str, str]):
	"""Сохранение файла с расписанием."""
	filename, link = (i for i in filename_and_link)
	if check_for_innovation(filename):
		response = requests.get(link)
		with open(PATH + filename, "wb") as schedule:
			schedule.write(response.content)
		convert(filename)
		return True


def parse():
	"""Проверка ответа сервера и запись данных в бд."""
	html = get_html(URL)
	if html.status_code == 200:
		if get_file(get_link_and_filename(html.text)):
			init_db(True)
			print("Расписание успешно обновлено!")
	else:
		print('Error')
		