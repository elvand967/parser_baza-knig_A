# -*- coding: cp1251 -*-

import random
import sys

import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from datetime import datetime

from utils import format_time, delete_file


def main():
    # проверка наличия торрент-файлов на страницах
    # update_torrent_presence_in_database(33894, 36210)  # Укажите контрольное число (9) и нужный диапазон id

    # уточним историю
    # update_old_torrent_there_torrent(1, 39999)
    update_torrent_presence_in_database(1, 39999)

    # count_books_with_there_torrent(1)

    # count_books_torrent(36000, 36999)

    pass




def update_torrent_presence_in_database_old(start_id, end_id):
    # Засекаем начало времени работы кода
    start_pars = time.time()
    # formatted_start_time = datetime.fromtimestamp(start_pars).strftime("%Y.%m.%d %H:%M")

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
        # Временно books.there_torrent = 9 - после проверки на наличие ссылки на торрент-файл = 8


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
                n += 1

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


def update_torrent_presence_in_database(start_id, end_id):
    # Засекаем начало времени работы кода
    start_pars = time.time()

    # Подключение к базе данных
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()
    n = 0
    nn = 0
    nnn = end_id - start_id + 1  # Общее количество итераций

    # Цикл по диапазону id
    for book_id in range(start_id, end_id + 1):
        # Инициализируем переменные перед блоком try
        id_books = None
        title = None
        link = None
        new_there_torrent = None

        # Получаем информацию из базы данных
        cursor.execute('SELECT * FROM books WHERE id = ? AND there_torrent = ?', (book_id, 9))
        book_info = cursor.fetchone()

        if book_info is None:
            continue
        else:
            id_books, title, link, there_torrent = book_info

            try:
                # Получаем HTML-код страницы
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Проверяем наличие тегов
                torrent_tags = soup.find_all('a',
                                             {'onclick': "yaCounter46924785.reachGoal('clickTorrent'); return true;"})

                # Определяем новое значение для there_torrent
                new_there_torrent = 8 if torrent_tags else 13

                # Обновляем столбец в базе данных
                cursor.execute('UPDATE books SET there_torrent = ? WHERE id = ?', (new_there_torrent, book_id))
                connection.commit()

                # Счетчик успешных итераций
                n += 1

            except Exception as e:
                print(f"Ошибка при обработке страницы {link}: {e}")
                continue

            # Случайная задержка от 0.5 до 1 секунды с шагом 0.1 секунды
            delay = round(random.uniform(0.5, 1.0), 1)
            time.sleep(delay)

        # Счетчик всех итераций
        nn += 1

        # Выводим результат
        end_pars = time.time()
        all_time = format_time(end_pars - start_pars)

        print(f"{n}/{nn}-{nnn} | {all_time} | torrent: {new_there_torrent} | id: {id_books} | {title}  {link}")

    # Закрываем соединение с базой данных
    connection.close()


'''
Функция для проработки истории
проверяет наличие учтенных торрент-файлов и в случае присутствия таковых
обновляет поле there_torrent
'''
def update_old_torrent_there_torrent(start_id, end_id):
    # Временно books.there_torrent = 9 - не проверен на наличие ссылки на торрент-файл

    if end_id is None:
        end_id = start_id
    if start_id > end_id:
        print( f'Некорректный диапозон id: start_id({start_id}) > end_id({end_id}) ')
        return
    # Подключение к базе данных
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()
    cursor.execute('''
    UPDATE books
    SET there_torrent = ?
    WHERE
        books.id IN (SELECT books.id
                     FROM books 
                     LEFT JOIN torrent ON books.link = torrent.link
                     WHERE torrent.link IS NOT NULL
                           AND books.id BETWEEN ? AND ?)
    ''', (1, start_id, end_id))
    connection.commit()

    # Закрываем соединение с базой данных
    connection.close()


'''
Подсчет количества записей
'''
def count_books_with_there_torrent(value):
    # Подключение к базе данных
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()

    # Выполнение SQL-запроса для подсчета строк
    cursor.execute('''
        SELECT COUNT(*) 
        FROM books 
        WHERE there_torrent = ?
        AND id >=? AND id <= ?
    ''', (value, 36000, 36999))

    # Получение результата и вывод в терминал
    count = cursor.fetchone()[0]
    print(f'Количество строк с there_torrent = {value}: {count}')

    # Закрытие соединения с базой данных
    connection.close()


'''
Подсчет количества записей 2
'''
def count_books_torrent(i, ii):
    # Подключение к базе данных
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()

    # Выполнение SQL-запроса для подсчета строк
    cursor.execute('''
        SELECT COUNT(*) 
        FROM torrent
        LEFT JOIN books ON torrent.link = books.link 
        WHERE
        books.id >=? AND books.id <= ?
    ''', (i, ii))

    # Получение результата и вывод в терминал
    count = cursor.fetchone()

    print(f'Количество строк для id от {i}  до {ii} с torrent: {count}')

    # Закрытие соединения с базой данных
    connection.close()


if __name__ == "__main__":
    main()