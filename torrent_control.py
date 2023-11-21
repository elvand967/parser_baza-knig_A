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
    # �������� ������ ������� ������ ����
    start_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_pars).strftime("%Y.%m.%d %H:%M")

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
                n +=1

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


# ������������� �������
update_torrent_presence_in_database(43050, 45999)  # ������� ������ �������� id

