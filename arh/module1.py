# D:\Python\myProject\parser_baza-knig\module1.py

import time
import random
import os
import json
import requests
from bs4 import BeautifulSoup

URL = 'https://baza-knig.ink/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
}


# Функция для сохранения в JSON
def save_to_json(comps, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(comps, file, ensure_ascii=False, indent=4)


def get_element_safe(soup, selector, index):
    elements = soup.select(selector)
    return elements[index].get_text(strip=True) if elements and len(elements) > index else 'Не найдено'


def parser(URL = URL, HEADERS = HEADERS):

    page = 5049
    filename = 'book_database_test.json'

    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            comps = json.load(file)
    else:
        comps = []

    while page:
        URLpage = URL + '/page/' + str(page)
        response = requests.get(URLpage, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.findAll('div', class_='short')

        for item in items:
            author_elem = get_element_safe(item, 'ul.reset.short-items li a', 0)
            read_book_elem = get_element_safe(item, 'ul.reset.short-items li a', 1)
            duration_elem = get_element_safe(item, 'ul.reset.short-items li b', 0)
            cycle_elem = get_element_safe(item, 'ul.reset.short-items li a', 2)
            genre_elems = item.select('ul.reset.short-items li a')[3:]

            comps.append({
                'page': page,
                'title': item.find('div', class_='short-title').get_text(strip=True),
                'author': author_elem,
                'read_book': read_book_elem,
                'duration': duration_elem,
                'cycle': cycle_elem,
                'genre': ', '.join([genre.get_text(strip=True) for genre in genre_elems]) if genre_elems else 'Не найдено',
                'link': item.find('div', class_='short-title').find('a').get('href'),
                'URL': URL,
            })

        print(f"Страница: {page}")

        save_to_json(comps, filename)

        t = random.randint(1, 3)
        print(f'Задержка {t} seconds')
        time.sleep(t)

        page = page - 1

if __name__ == "__main__":
    parser()
