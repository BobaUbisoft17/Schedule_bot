from typing import Optional, Tuple
import requests
from requests import Response
from bs4 import BeautifulSoup
from schedule_bot import convert
from schedule_SQL import init_db
import glob
import os

URL = 'https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov'
HEADERS = {
	'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
	'accept' : '*/*',
}


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
	r = requests.get(url, headers=HEADERS, params=params)
	return r


def get_schedule_link(html: str) -> Tuple[str, str]:
	soup = BeautifulSoup(html, 'lxml')
	schedules_and_link = {}
	schedules = soup.find_all('a', class_='at_url')[-1]
	return schedules.get('href').split("/")[-1], schedules.get('href')


def get_file(path_and_link: Tuple[str, str]):
	path, link = (i for i in path_and_link)
	if check_for_innovation(path):
		response = requests.get(link)
		with open(path, "wb") as schedule:
			schedule.write(response.content)
		convert(path)
		return True


def parse():
	html = get_html(URL)
	if html.status_code == 200:
		if get_file(get_schedule_link(html.text)):
			return True
	else:
		print('Error')
		