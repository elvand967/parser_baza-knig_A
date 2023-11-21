# -*- coding: cp1251 -*-
import random
import sys

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime

from utils import format_time


def update_torrent_presence_in_database(start_id, end_id):
    # Засекаем начало времени работы кода
    start_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_pars).strftime("%Y.%m.%d %H:%M")

    # Подключение к базе данных
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()
    n = 0
    nn = 0
    # Общее количество итераций
    nnn = end_id - start_id + 1

    # Цикл по диапазону id
    for book_id in range(start_id, end_id + 1):
        # Получаем информацию из базы данных
        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book_info = cursor.fetchone()

        if book_info:
            id_books, title, link, there_torrent = book_info
            # print(f"Обрабатывается строка {book_id}: id_books={id_books}, title={title}, link={link}")

            try:
                # Получаем HTML-код страницы
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Проверяем наличие тегов
                torrent_tags = soup.find_all('a',
                                             {'onclick': "yaCounter46924785.reachGoal('clickTorrent'); return true;"})

                # Обновляем столбец в базе данных
                cursor.execute('UPDATE books SET there_torrent = ? WHERE id = ?', (int(bool(torrent_tags)), book_id))
                connection.commit()
                # Счетчик успешных итераций
                n +=1

            except Exception as e:
                continue
                print(f"Ошибка при обработке страницы {link}: {e}")

            # Случайная задержка от 0.5 до 1 секунд с шагом 0.1 секунд
            delay = round(random.uniform(0.5, 1.0), 1)
            time.sleep(delay)

        # Счетчик всех итераций
        nn += 1
        # Выводим результат
        end_pars = time.time()
        # Посчитаем время затраченное на парсинг URL
        # и с помощью функции format_time(seconds) вернем в формате  "hh:mm:ss"
        all_time = format_time(end_pars - start_pars)
        print(f"{n}/{nn}-{nnn}| {all_time} | torrent: {int(bool(torrent_tags))} | id: {id_books} | {title}  {link}")

    # Закрываем соединение с базой данных
    connection.close()


# использования функции
update_torrent_presence_in_database(43050, 45999)  # Укажите нужный диапазон id

