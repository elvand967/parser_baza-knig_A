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
    # �������� ������� �������-������ �� ���������
    # update_torrent_presence_in_database(33894, 36210)  # ������� ����������� ����� (9) � ������ �������� id

    # ������� �������
    # update_old_torrent_there_torrent(1, 39999)
    update_torrent_presence_in_database(1, 39999)

    # count_books_with_there_torrent(1)

    # count_books_torrent(36000, 36999)

    pass




def update_torrent_presence_in_database_old(start_id, end_id):
    # �������� ������ ������� ������ ����
    start_pars = time.time()
    # formatted_start_time = datetime.fromtimestamp(start_pars).strftime("%Y.%m.%d %H:%M")

    # ����������� � ���� ������
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()
    n = 0
    nn = 0
    # ����� ���������� ��������
    nnn = end_id - start_id + 1


    # ���� �� ��������� id
    for book_id in range(start_id, end_id + 1):
        # �������� ���������� �� ���� ������
        # �������� books.there_torrent = 9 - ����� �������� �� ������� ������ �� �������-���� = 8


        cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
        book_info = cursor.fetchone()

        if book_info:
            id_books, title, link, there_torrent = book_info
            # print(f"�������������� ������ {book_id}: id_books={id_books}, title={title}, link={link}")

            try:
                # �������� HTML-��� ��������
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')

                # ��������� ������� �����
                torrent_tags = soup.find_all('a',
                                             {'onclick': "yaCounter46924785.reachGoal('clickTorrent'); return true;"})

                # ��������� ������� � ���� ������
                cursor.execute('UPDATE books SET there_torrent = ? WHERE id = ?', (int(bool(torrent_tags)), book_id))
                connection.commit()
                # ������� �������� ��������
                n += 1

            except Exception as e:
                continue
                print(f"������ ��� ��������� �������� {link}: {e}")

            # ��������� �������� �� 0.5 �� 1 ������ � ����� 0.1 ������
            delay = round(random.uniform(0.5, 1.0), 1)
            time.sleep(delay)

        # ������� ���� ��������
        nn += 1
        # ������� ���������
        end_pars = time.time()
        # ��������� ����� ����������� �� ������� URL
        # � � ������� ������� format_time(seconds) ������ � �������  "hh:mm:ss"
        all_time = format_time(end_pars - start_pars)
        print(f"{n}/{nn}-{nnn}| {all_time} | torrent: {int(bool(torrent_tags))} | id: {id_books} | {title}  {link}")

    # ��������� ���������� � ����� ������
    connection.close()


def update_torrent_presence_in_database(start_id, end_id):
    # �������� ������ ������� ������ ����
    start_pars = time.time()

    # ����������� � ���� ������
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()
    n = 0
    nn = 0
    nnn = end_id - start_id + 1  # ����� ���������� ��������

    # ���� �� ��������� id
    for book_id in range(start_id, end_id + 1):
        # �������������� ���������� ����� ������ try
        id_books = None
        title = None
        link = None
        new_there_torrent = None

        # �������� ���������� �� ���� ������
        cursor.execute('SELECT * FROM books WHERE id = ? AND there_torrent = ?', (book_id, 9))
        book_info = cursor.fetchone()

        if book_info is None:
            continue
        else:
            id_books, title, link, there_torrent = book_info

            try:
                # �������� HTML-��� ��������
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')

                # ��������� ������� �����
                torrent_tags = soup.find_all('a',
                                             {'onclick': "yaCounter46924785.reachGoal('clickTorrent'); return true;"})

                # ���������� ����� �������� ��� there_torrent
                new_there_torrent = 8 if torrent_tags else 13

                # ��������� ������� � ���� ������
                cursor.execute('UPDATE books SET there_torrent = ? WHERE id = ?', (new_there_torrent, book_id))
                connection.commit()

                # ������� �������� ��������
                n += 1

            except Exception as e:
                print(f"������ ��� ��������� �������� {link}: {e}")
                continue

            # ��������� �������� �� 0.5 �� 1 ������� � ����� 0.1 �������
            delay = round(random.uniform(0.5, 1.0), 1)
            time.sleep(delay)

        # ������� ���� ��������
        nn += 1

        # ������� ���������
        end_pars = time.time()
        all_time = format_time(end_pars - start_pars)

        print(f"{n}/{nn}-{nnn} | {all_time} | torrent: {new_there_torrent} | id: {id_books} | {title}  {link}")

    # ��������� ���������� � ����� ������
    connection.close()


'''
������� ��� ���������� �������
��������� ������� �������� �������-������ � � ������ ����������� �������
��������� ���� there_torrent
'''
def update_old_torrent_there_torrent(start_id, end_id):
    # �������� books.there_torrent = 9 - �� �������� �� ������� ������ �� �������-����

    if end_id is None:
        end_id = start_id
    if start_id > end_id:
        print( f'������������ �������� id: start_id({start_id}) > end_id({end_id}) ')
        return
    # ����������� � ���� ������
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

    # ��������� ���������� � ����� ������
    connection.close()


'''
������� ���������� �������
'''
def count_books_with_there_torrent(value):
    # ����������� � ���� ������
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()

    # ���������� SQL-������� ��� �������� �����
    cursor.execute('''
        SELECT COUNT(*) 
        FROM books 
        WHERE there_torrent = ?
        AND id >=? AND id <= ?
    ''', (value, 36000, 36999))

    # ��������� ���������� � ����� � ��������
    count = cursor.fetchone()[0]
    print(f'���������� ����� � there_torrent = {value}: {count}')

    # �������� ���������� � ����� ������
    connection.close()


'''
������� ���������� ������� 2
'''
def count_books_torrent(i, ii):
    # ����������� � ���� ������
    connection = sqlite3.connect('book_database.db')
    cursor = connection.cursor()

    # ���������� SQL-������� ��� �������� �����
    cursor.execute('''
        SELECT COUNT(*) 
        FROM torrent
        LEFT JOIN books ON torrent.link = books.link 
        WHERE
        books.id >=? AND books.id <= ?
    ''', (i, ii))

    # ��������� ���������� � ����� � ��������
    count = cursor.fetchone()

    print(f'���������� ����� ��� id �� {i}  �� {ii} � torrent: {count}')

    # �������� ���������� � ����� ������
    connection.close()


if __name__ == "__main__":
    main()