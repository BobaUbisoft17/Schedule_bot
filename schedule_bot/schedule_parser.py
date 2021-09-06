import requests
from bs4 import BeautifulSoup
from schedule_bot import convert

URL = 'https://s11018.edu35.ru/obuchayushchimsya/raspisanie-urokov'
HEADERS = {
	'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
	'accept' : '*/*',
}
PATH = 'csv_schedule/'


def get_html(url, params=None):
	r = requests.get(url, headers=HEADERS, params=params)
	return r


def get_schedule_link(html):
	soup = BeautifulSoup(html, 'lxml')
	schedules_and_link = {}
	schedules = soup.find_all('a', class_='at_url')[-1]
	return schedules.get('href').split("/")[-1], schedules.get('href')


def get_file(path_and_link):
	path, link = (i for i in path_and_link) 
	r = requests.get(link)
	with open(PATH + path, "wb") as schedule:
		schedule.write(r.content)
	convert(path)


def parse():
	html = get_html(URL)
	if html.status_code == 200:
		get_file(get_schedule_link(html.text))
	else:
		print('Error')
