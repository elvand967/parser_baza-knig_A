# -*- coding: cp1251 -*-
# D:\Python\myProject\parser_baza-knig_A\module3_A.py

'''
������ ������ ������ �������� "���������" (details)

'''
# import mimetypes
import os
import re
import sqlite3
import time
import random
# pip install requests
import requests
# pip install requests bs4
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

from utils import clean_filename

# ���������� � ������� �������� ����������� ������ 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))

def main():
    # ������ �������� ��� ��������
    List_dict_parsing = new_details_parsing_package()

    for item in List_dict_parsing:
        # print(item["link"])
        parser(item["id"], item["title"], item["link"])
        # ��������� �������� �� 0.5 �� 2 ������ � ����� 0.1 ������
        delay = round(random.uniform(0.5, 2.0), 1)
        time.sleep(delay)


'''������� ����� `����� ��������` <details> '''
def new_details_parsing_package():
    global path_current_directory

    print('������� ����� `����� �������`\n�������: ' )
    # �������� ��������� n � x
    n = int(input("��������� id ��������� ������� `books`: "))
    m = int(input("��������  id ��������� ������� `books`: "))
    if m < n:
        m = n

    # ������� ������ ���� � "book_database.db"
    name_db = "book_database.db"
    name_db_path = os.path.join(path_current_directory, name_db)

    # ������������� ���������� � ����� ������
    conn = sqlite3.connect(name_db_path)
    cursor = conn.cursor()

    # ��������� SQL-������ ��� ������� ������
    # books.id, books.title, books.link ��� ����� �������
    # ���� ������ � ������� `torrent` � ����������� ������ � ������� `details`
    cursor.execute(
        '''
        SELECT books.id, books.title, books.link
        FROM books
        JOIN torrent ON books.link = torrent.link
        LEFT JOIN details ON books.id = details.id_books
        WHERE books.id BETWEEN ? AND ?
          AND details.id IS NULL;
        ''',
        (n, m))

    # ��������� ��������� ������
    rows = cursor.fetchall()

    # ��������� ����������
    conn.close()

    # ������� ������ �������� �� ������ ��������� �����
    data = []
    for row in rows:
        id, title, link = row
        data.append({
            "id": id,
            "title": title,
            "link": link,
        })
        # print(row)

    return data


def key_translation(ru_key):
    translation_dict = {
        '�����': 'author',
        '������': 'reading',
        '���': 'year',
        '������������': 'duration',
        '��������': 'quality',
        '����': 'cycle',
        '������': 'size',
        '����': 'genre'
    }
    return translation_dict.get(ru_key, ru_key)


def save(comps):
    with open('pars01_info.txt', 'a') as file:
        for comp in comps:
            file.write(f"{comp['title']}\n��������: {comp['text']}\n������: {comp['link']}\n\n")


'''
������� ��������� �������� ��� �������� � ��������� ������� � ������������
'''
def parser(id_books, title, url):
    # �������� ���������� � ������� ����� ������� ����� �����, ������� ����� �������
    url_base = 'https://baza-knig.ink/'

    # � ���������� �������� ����-�����, ���-�� ������� �� ������ ���� ��������� ��� �������� ����
    # HEADERS = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    # }
    # HEADERS = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0 (Edition Yx 03)'
    # }
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0 (Edition Yx 03)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.41 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.41",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.277",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Vivaldi/4.1.2369.21",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.41",
    ]

    # �������� ������ �� ������
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            HEADERS = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=HEADERS, timeout=3)
            response.raise_for_status()  # ���������, ��� �� �������� ������
            break  # ����� �� �����, ���� ������ ������ �������
        except Timeout as e:
            retries += 1
            if retries < max_retries:
                print(f"������:\n{e}.\n��������� ������� ����� 3 ������ (������� {retries}/{max_retries}).")
                time.sleep(3)
            else:
                print(f"���������� ������������ ���������� �������. ���������� ��������� �������.")
                return
        except Exception as e:
            print(f"����������� ������:\n{e}")
            return



    soup = BeautifulSoup(response.content, 'html.parser')
    comps = {}
# -----------------------------------------------
    # ����� ���������� �� �����
    items = soup.find('ul', class_="reset full-items")
    if items:
        li_items = items.find_all('li')
        for li in li_items:
            key = li.contents[0].strip().rstrip(':')
            value = li.contents[1].text.strip()
            comps[key_translation(key)] = value
# -----------------------------------------------
    # ��������� �������� ����� �� <div> � ������� "short-text"
    description = soup.find('div', class_="short-text").get_text(strip=True)
    if description:
        # ����������� �������� � ������� ���������� ��������� Get re
        # �������� �����, ������� � ������� ������� "\n" � �����
        description = re.sub(r'\n.*', '', description)

        # �������� ����� �� "������ ��������:", ������� ���� �����.
        description = re.sub(r'^.*?������ ��������:', '', description, flags=re.DOTALL)

        # �������� ���������� �������� � ������� �������� ������ � ������ � �����
        description = description.strip()
        # ��������� `����` � �������
        comps['description'] = description
# -----------------------------------------------
    # �������� ������ ��� ��������
    img_element = soup.find("div", class_="full-img")
    if img_element and 'src' in img_element.img.attrs:
        img_url = img_element.img['src']
        # img_ext = img_url.split(".")[-1]  # ������� ���������� ��������

        # ��������� ������� � URL
        img_url = url_base + img_url

        # ��������� ��������
        picture = download_image(response, img_url, id_books, title)
        if picture is not None:
            comps['path_picture'] = picture[0]
            comps['picture'] = picture[1]
# -----------------------------------------------




    print(comps)


# ������� ��� �������� � ���������� ��������
def download_image(response, url, id_books, title):
    # �������� ���� � ����� ����e ��������
    path_shared_images_folder = os.path.join(path_current_directory, "Downloads_picture")
    if not os.path.exists(path_shared_images_folder):
        os.makedirs(path_shared_images_folder)  # ������� ����������, ���� ��� �� ����������

    # ��������� ��� ������������� �����
    path_picture = str(id_books // 1000)

    # ������ ���� � ������������� �����
    download_dir = os.path.join(path_shared_images_folder, path_picture)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)  # ������� ����������, ���� ��� �� ����������

    # ��������� ����� ��� �����������
    img_ext = url.split(".")[-1]  # ������� ���������� �������� �� url
    filename = f'{clean_filename(title).replace(" ", "_")}_{id_books}.{img_ext}'
    filepath = os.path.join(download_dir, filename)

    # ��������� ��������
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return [path_picture, filename]



if __name__ == "__main__":
    main()