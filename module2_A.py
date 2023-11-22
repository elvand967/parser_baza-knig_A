# -*- coding: cp1251 -*-
# D:\Python\myProject\parser_baza-knig_A\module2_A.py

'''
� ���� ������ ��������� �������-�����, ��������� �� web-���������
URL ������� ��������� �� book_database.db books (link).
��� ��� ��������� ������ �� �������-����� � ������� ������ � book_database.db torrent (torrent) ���.

���-����� ����� � ������� ������� my_print(name_path, text)

'''





import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime
import winreg  # ��� ������� � ������� Windows ��� ������������� ��������� ���� � ����� �������� ��������� �� ���������
import random

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from datetime import datetime
# from unidecode import unidecode
from utils import get_default_download_directory, clean_filename, \
    read_json_file, my_print, get_files_in_directory, remove_replace_substring_postfix, delete_file, format_time, \
    write_json_file

# ���������� � ������� �������� ����������� ������ 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))

# ���� � ����� downloads ������� windows ������� � ������� ����� �������
download_folder = get_default_download_directory()

# ���� � ����� downloads ���������, ��� ���������� � �������� ��������������� �������-������
path_dir_downloads_torrent = ''

# ��������� ��� ���-����� MY_LOG
now = datetime.now()
script_path = os.path.basename(sys.argv[0])
script_name, _ = os.path.splitext(script_path)
MY_LOG = now.strftime("%Y-%m-%d_%H-%M_") + script_name + ".txt"

def main():
    # ��������� �������� ����������
    # ���������� � ������� �������� ����������� ������ 'module2_A.py '
    global path_current_directory

    path_dir_Get = os.path.join(path_current_directory, "JSONfiles\\Get")
    if not os.path.exists(path_dir_Get):
        os.makedirs(path_dir_Get)  # ������� ����������, ���� ��� �� ����������
    path_dir_Set = os.path.join(path_current_directory, "JSONfiles\\Set")
    if not os.path.exists(path_dir_Set):
        os.makedirs(path_dir_Set)  # -//-

    global path_dir_downloads_torrent
    path_dir_downloads_torrent = os.path.join(path_current_directory, "Downloads_torrent")
    if not os.path.exists(path_dir_downloads_torrent):
        os.makedirs(path_dir_downloads_torrent)  # -//-

    path_log_files = os.path.join(path_current_directory, "Log_files")
    if not os.path.exists(path_log_files):
        os.makedirs(path_log_files)  # -//-

    global MY_LOG
    MY_LOG = os.path.join(path_log_files, MY_LOG)

    # �������� ������ ������� ������ ����
    start_time_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time_pars).strftime("%Y.%m.%d %H:%M")

    global script_name
    my_print(MY_LOG, f'{formatted_start_time} ����� ������� {script_name}')

    # ��������� ���� "����� ������ �������"
    menu_mode = menu_script_mode()
    if menu_mode == 1:  # �����: "������ �������� (��������� JSON, �������� ������� ������)"
        # ������� ���� ������ ������� ��������
        path_GetJson_download_package = menu_packages_downloads(path_dir_Get, menu_mode)

        # ���� ������� ��� ������� ���� � *.json ����� ������ �������� ���������
        if path_GetJson_download_package is not None:
            general_functions_torrent(path_GetJson_download_package)

    elif menu_mode == 2:  # '�����: "����������� ����������� ������ � ��"'
        # ������� ���� ������ ������� ��������
        path_SetJson_download_package = menu_packages_downloads(path_dir_Set, menu_mode)

        # ���� ������� ��� ������� ���� � *.json ����� ������ �������� � ���� ������
        if path_SetJson_download_package is not None:
            # print( f'������� ��������� �� �� {path_SetJson_download_package}')
            general_functions_torrent_db(path_SetJson_download_package)

    elif menu_mode == 3:  # '�����: "������ ����������� �������-������ *.db - Downloads_torrent"'
        downloads_path_torrent = 'Downloads_torrent'
        compare_torrent_files_with_database(downloads_path_torrent, 'book_database.db')


# ����: ����� ������ �������
def menu_script_mode():
    print('������ ������ �������:\n****************')
    print('  1: ������ �������� (��������� JSON, �������� ������� ������)')
    print('  2: ����������� ����������� ������ � ��')
    print('  3: ������ ����������� �������-������ � ��\n****************')
    recd = int(input("������� � ������ ������: "))
    if recd == 1:
        my_print(MY_LOG, '�����: "������ �������� (��������� JSON, �������� ������� ������)"')
        return 1
    elif recd == 2:
        my_print(MY_LOG, '�����: "����������� ����������� ������ � ��"')
        return 2
    elif recd == 3:
        my_print(MY_LOG, '�����: "������ ����������� �������-������ *.db - Downloads_torrent"')
        return 3


# ������� ����, �����: "������ �������� (��������� JSON, �������� ������� ������)"
def menu_packages_downloads(path_dir, menu_mode):
    while True:
        # ������� ������ *.json ������ ����������� � �������� ���������� `path_dir`
        # ��������� ������� `get_files_in_directory(dir_path)`
        list_json = get_files_in_directory(path_dir, '.json')
        if len(list_json):
            print('\n�������� JSON-����� `������� ��������`:\n---------------------')
            # � ����� ��������� ��� JSON-����� � �������� ���������� `path_dir`
            for i, file in enumerate(list_json):
                # ������� ������ ���� � �����
                file_path = os.path.join(path_dir, file)
                # � ������� ������� read_json_file(path_json_download_package)
                # ������� ���, ����������� ��������� ������ ��� ��������
                # ���-�� ��������� ���-�� ���� ��������
                list_dict_json = read_json_file(file_path)
                if len(list_dict_json) == 0:
                    delete_file(path_dir, file)
                    continue
                print(f'  {i} : {file}\t [{len(list_dict_json)}]')
        else:
            print('---------------------\n  ��� ��������� JSON-������ `������� ��������`')

        print('  -------------------')
        if menu_mode == 1:
            print('  N : ������� ����� `����� ��������` (New)')
        print('  X : ����� (Exit)\n---------------------')

        recd = input("������� ������ `������ ��������` ���\n����� ��� ��������������� ��������: ")

        if recd.isdigit():  # ���� ������ ������� �� ����
            i = int(recd)  # �������� � ���������������� ����
            if 0 <= i < len(list_json):  # � �������� ������ �� ���������� (����������) ������
                my_print(MY_LOG, f'\n����� ��������: {list_json[i]}')
                # �������� ������ ���� � ����� ������ ��������
                selected_path_file = os.path.join(path_dir, list_json[i])
                return selected_path_file

        elif recd.isalpha():  # ���� ������ ������� �� ����
            if len(recd) == 1:
                if menu_mode == 1 and (recd.upper() == 'N' or recd.upper() == '�'):
                    # �������� ������� �������� ������ ������ ��������
                    create_json_with_no_torrent(path_dir)
                    continue
                elif recd.upper() == 'X' or recd.upper() == '�':
                    print('�����')
                    sys.exit()  # ������� �� ���������

        else:
            # ���� ���� �����, �������� �������
            print('������������ ����! ��������� �������.')


'''������� ����� `����� ��������`'''
def create_json_with_no_torrent(path_dir_Get):
    global path_current_directory
    global MY_LOG

    print('������� ����� `����� ��������`\n�������: ' )
    # �������� ��������� n � x
    n = int(input("��������� id ��������� ������� `books`: "))
    m = int(input("��������  id ��������� ������� `books`: "))
    if m < n:
        m = n

    # ���������� ��� JSON-�����
    file_json_name = f'Get_torrent({n}-{m}).json'

    # ������� ������ ���� � "book_database.db"
    name_db = "book_database.db"
    name_db_path = os.path.join(path_current_directory, name_db)

    # ������������� ���������� � ����� ������
    conn = sqlite3.connect(name_db_path)
    cursor = conn.cursor()

    # ��������� SQL-������ ��� ������� ������

    # cursor.execute(
    #     '''
    #     SELECT books.id, books.title, books.link
    #     FROM books
    #     LEFT JOIN torrent ON books.link = torrent.link
    #     WHERE books.id >= ? AND books.id <= ? AND (torrent.link IS NULL OR torrent.torrent IS NULL OR torrent.torrent = "Null")
    #     ''',
    #     (n, m))


    # ��������� SQL-������.
    # ������ �� ��������� ������ ���������� ��������� ��� �������
    # ��� ������� � ��������� � books ������� torrent
    # � � ������� �������� ������� ����� "1"
    cursor.execute(
        '''
        SELECT books.id, books.title, books.link
        FROM books
        LEFT JOIN torrent ON books.link = torrent.link
        WHERE 
            books.id >= ? AND books.id <= ? AND 
            (torrent.link IS NULL OR torrent.torrent IS NULL OR torrent.torrent = "Null") AND
            books.there_torrent = ?
        ''',
        (n, m, 1))


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

    # ������� ���� � ������� ������ � *.json ����
    file_path = os.path.join(path_dir_Get, file_json_name)
    write_json_file(file_path, data)
    my_print(MY_LOG, f'������ `����� ��������`: {file_json_name}')


''' ����� ������� ����������� �������� �������-������.
��������� ������ ���� � ��������� JSON-�����, ��������� ������ ��������
���������� ��������� �������� download_torrent_file(page_url) 
�� �������� ������� �� �������-������
'''
def general_functions_torrent(path_GetJson_download_package):
    # ������� ���������� ��������� JSON-����� � ���� ������ ��������
    list_dict_json_Get = read_json_file(path_GetJson_download_package)
    # ���� �� ���������� ��������� �������� JSON-����
    if list_dict_json_Get is None:
        print('��������� ������� ������� � ��������� JSON ����.\n�����')
        sys.exit()  # ������� �� ���������

    # �������� ������ ���� � ������ ��������� JSON ����� (~Set_torrent(...-...).json)
    # ������� � ������ ���� � ����� ����� `Get` �� `Set`
    path_SetJson_download_package =remove_replace_substring_postfix(path_GetJson_download_package, 'Get', 'Set')
    # �������� JSON ���� (~Set_torrent(...-...).json) � ������ ������� ��� ��������� ���� ����
    list_dict_json_Set = read_json_file(path_SetJson_download_package)

    len_Get_json = len(list_dict_json_Get)
    my_print(MY_LOG, f'���������� ��������� � �������� Get~.json: {len_Get_json}')
    my_print(MY_LOG, f'���������� ��������� � �������� Set~.json: {len(list_dict_json_Set)}\n')

    # �������� ������ ������� ������ ����
    start_time_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time_pars).strftime("%Y.%m.%d %H:%M")
    my_print(MY_LOG, f'����� ������ �������� �������-������: {formatted_start_time}')

    items_dict = list(list_dict_json_Get)

    # ������� ����������� �������-������
    sum_torrent = 0

    # �������� ������� �������-�����
    for i, item in enumerate(items_dict):
        # �������� ����� ��������� URL - ������� ��������
        start_time_URL = time.time()

        page_url = item["link"]
        # �������� download_torrent_file ��� �������� �������-�����
        torrent_file = download_torrent_file(page_url)

        my_print(MY_LOG, f'\n�������� �������-����� �: {i + 1} �� {len_Get_json}')
        # print(f'id_db: {item["id"]}, ����� `{item["title"]}`.')

        # ��������� ��������� ������ �������
        # (��� �������-����� ���� ��������� �� ������)
        if torrent_file is None:
            end_time_URL = time.time()
            # ��������� ���������� ������ ����������� �� ��������� URL
            # � � ������� ������� format_time(seconds) ������ � �������  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)
            all_time =  format_time(end_time_URL - start_time_pars)

            my_print(MY_LOG,
                     f'!!! ��������� ������� �������� �������-�����,'
                     # f'\nid_db: {item["id"]}, ����� `{item["title"]}`.'
                     f'\n����� ��������� URL: {elapsed_time_URL}/{all_time}'
                     f'\n����� ��������� {sum_torrent}/{i + 1}-{len_Get_json}')
            continue
        else:
            # ��������� ��� ������������ �������-�����
            item["torrent_old"] = torrent_file

            # ������� ���������������� � ���������� �� ����������� �������-������
            new_torrent_file = fixing_new_torrent_path(torrent_file, item["id"], item["title"])

            if new_torrent_file is not None:
                item["torrent"] = new_torrent_file["torrent"]
                item["path_torrent"] = new_torrent_file["path_torrent"]

            # ��� �������� �������� �������-����� ������ ��������� � ������ ��������
            list_dict_json_Set.append(item)  # ������� ����� �������
            list_dict_json_Get.remove(item)  # ������ ������ �������

            # ��������� SetJson-����
            write_json_file(path_SetJson_download_package, list_dict_json_Set)

            # ��������� GetJson-����
            write_json_file(path_GetJson_download_package, list_dict_json_Get)

            # �� ������� ��������� �������� ��������
            sum_torrent += 1

            end_time_URL = time.time()
            # ��������� ���������� ������ ����������� �� ��������� URL
            # � � ������� ������� format_time(seconds) ������ � �������  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)
            all_time = format_time(end_time_URL - start_time_pars)
            my_print(MY_LOG,
                     # f'������� ��������: {torrent_file},\n'
                     # f'����� `{item["title"]}`, id_db: {item["id"]}.\n'
                     f'����� ��������� URL: {elapsed_time_URL}/{all_time}\n'
                     f'����� ��������� {sum_torrent}/{i + 1}-{len_Get_json}')

        # ��������� �������� �� 1.0 �� 1.5 ������ � ����� 0.1 ������
        random_uni = round(random.uniform(1.0, 1.5), 1)
        time.sleep(random_uni)

    end_time_pars = time.time()
    elapsed_time_pars = end_time_pars - start_time_pars
    elapsed_time_formatted = format_time(elapsed_time_pars)

    my_print(MY_LOG, f"\n\n�� ��������� {len_Get_json} ���������, ����� ���������: {elapsed_time_formatted}")
    my_print(MY_LOG, f"���������: {sum_torrent} �������-������")
    my_print(MY_LOG, f'\n����:'
                     f'\n- � �������� `Get~.json` �������� �� ���������� ���������: {len(list_dict_json_Get)}')
    my_print(MY_LOG, f'- � �������� `Set~.json` ���������� ���������: {len(list_dict_json_Set)}\n\n\n\n')


''' ������� ���������� �������-����� � URL '''
def download_torrent_file(url):
    try:
        # ���� � ����� downloads ������� � ������� ����� �������
        global download_folder

        # �������� ������ ������ �� ���������� � ����� ����� �������� ���������
        filenames_old = set(os.listdir(download_folder))

        # ���������� Google Chrome ��� ���������� �������-�����
        driver = webdriver.Chrome()

        driver.get(url)  # ��������� ��������

        # wait = WebDriverWait(driver, 60)  # ����������� ����� �������� +???
        WebDriverWait(driver, 60)  # ����������� ����� �������� +???

        # ���������� JavaScript ��� ��������� �������� ���� �� �����
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # ������ ����� ���������� ���������� �������-�����

        # ��������� ������� ������ �� �������
        if driver.find_elements(By.CSS_SELECTOR,
                                "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]"):
            torrent_link_url = driver.find_element(By.CSS_SELECTOR,
                                                   "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]")

            # ������� �� ������ ��������
            torrent_link_url.click()

            # wait = WebDriverWait(driver, 60)  # ����������� ����� ��������
            WebDriverWait(driver, 60)  # ����������� ����� ��������

            # # �������� 1-2 �������
            # t1 = random.randint(1, 2)
            # time.sleep(t1)

            #  ��������� ������� ����������� ����, �������� ������� ������� "f12"
            pyautogui.press('f12')

            # �������� ���
            # ��������� �������� �� 1.0 �� 1.5 ������ � ����� 0.1 ������
            t2 = round(random.uniform(1.0, 1.5), 1)
            time.sleep(t2)

            # # �������� �������� �����  -???
            # try:
            #     wait.until(lambda x: any(filename.endswith('.torrent') for filename in os.listdir(download_folder)))
            # except TimeoutException:
            #     # print("�������-���� �� ��������.")
            #     return None

            # �������� ������ ������ ����� ����������
            filenames_new = set(os.listdir(download_folder))

            # ������� ��� ������ �����
            downloaded_file = next(iter(filenames_new - filenames_old), None)
            if downloaded_file is not None:
                # ��������� ������� ����� ����������
                driver.quit()
                return downloaded_file

        else:
            my_print(MY_LOG, f"������� �� ������ �� ��������")
            driver.quit()
            return None

    except Exception as e:
        my_print(MY_LOG, f"������ ��� ���������� �������-�����: {e}")
        # driver.quit()
        return None


''' ������� ��������� ��� ������������ ����� � id books
 �������� ��� � ������������� ���������� � ���������������.
 ��������� ������� � ������, ����� ������ � ����� � ����
 ������� ����� ��������� ����'''
def fixing_new_torrent_path(torrent_file, id_books, title):
    global download_folder  # ����� �������� ������ �� ���������, ��������� ������� windows
    global path_dir_downloads_torrent  # ����� ����� �������� ������ �������

    # ��������� ��� ������������� �����
    subdirectory = str(id_books // 1000)
    # �������� ������ ���� � ������������� ����e
    subdirectory_path = os.path.join(path_dir_downloads_torrent, subdirectory)
    # ���������, ���������� �� ��������� ����������
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)  # ������� ����������, ���� ��� �� ����������

    # ��������� ����� ��� �������-�����
    new_name_torrent_file = f'{clean_filename(title).replace(" ", "_")}_{id_books}.{torrent_file.split(".")[-1]}'

    # ������ ���� � ��������� �������-�����
    source_torrent_file_path = os.path.join(download_folder, torrent_file)

    # ������ ���� � ������, ���������������� �������-�����
    destination_torrent_file_path = os.path.join(subdirectory_path, new_name_torrent_file)

    try:
        # �������� �������-���� � ��������������� ���
        shutil.copy2(source_torrent_file_path, destination_torrent_file_path)
        my_print(MY_LOG, f'�������-���� ������� �������� � ������������:\n`{new_name_torrent_file}`')

        result = {"torrent": new_name_torrent_file,
                  "path_torrent": subdirectory
                  # "path_torrent": destination_torrent_file_path
                  }

        # ������� ������� ��� �������� ������������ �����
        # � ����� �������� ������ �� ���������, ��������� ������� windows
        delete_file(download_folder, torrent_file)

        return result

    except Exception as e:
        print(f'������ ��� ����������� �������-�����: {e}')
        return None


''' ����� ������� �������� �������-������ � ��.
��������� ������ ���� � Set JSON-�����, ��������� ������ ��������
���������� ��������� �������� ???
'''
def general_functions_torrent_db(path_SetJson_download_package):
    # ������� ���������� ��������� JSON-����� � ���� ������ ��������
    list_dict_json_Set = read_json_file(path_SetJson_download_package)
    # ���� �� ���������� ��������� �������� JSON-����
    if list_dict_json_Set is None:
        print('��������� ������� ������� � ��������� JSON ����.\n�����')
        sys.exit()  # ������� �� ���������
    my_print(MY_LOG, f'���������� �������� � Set~.json: {len(list_dict_json_Set)}\n')

    # �������� �������������� �������-����� � ��
    # ����������� � ���� ������
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # ��������
    successful_attempts = 0
    failed_attempts = 0

    for record in list_dict_json_Set:
        link = record.get("link")
        torrent = record.get("torrent")

        # ��������� ������� ������ � ����� ������ ��� ���������
        cursor.execute('SELECT * FROM torrent WHERE link = ? OR torrent = ?', (link, torrent))
        existing_record = cursor.fetchone()

        if existing_record:
            # ����������, ����� ���� ������� ������������
            duplicate_field = "link" if existing_record[1] == link else "torrent"
            print(f'������ � ����������� ��������� ���� {duplicate_field} ({existing_record[1]})\n'
                  f'��� ����������. ���������� ���������� � ������� "torrent".\n')
            failed_attempts += 1
            continue
        else:
            # ��������� ����� ������, ��� ��� ������ � ����� ������ �� ����������
            cursor.execute('''
                INSERT INTO torrent (link, torrent_old, torrent, path_torrent)
                VALUES (?, ?, ?, ?)
            ''', (link, record.get("torrent_old"), torrent, record.get("path_torrent")))
            successful_attempts += 1

    # ��������� ��������� � ��������� ����������
    conn.commit()
    conn.close()

    # ������� ���������
    print(f'������� ��������� ������� � db: {successful_attempts}')
    print(f'��������� ������� ���������� � db: {failed_attempts}')
    print(f'����� ������� ���������� � db: {successful_attempts + failed_attempts}')


def compare_torrent_files_with_database(directory_path, database_path):
    # �������� ������ ������������� � Downloads_torrent
    subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    # ������������ � ���� ������ SQLite
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(directory_path, subdirectory)

        # �������� ������ ������ � �������������
        files_in_directory = [f for f in os.listdir(subdirectory_path) if os.path.isfile(os.path.join(subdirectory_path, f))]

        # SQL-������ ��� ��������� ������ ���� �������-������ ��� ������ �������������
        sql_query = f"SELECT path_torrent, torrent FROM torrent WHERE path_torrent = ?"
        cursor.execute(sql_query, (subdirectory,))

        # �������� ��������� �������
        database_files = cursor.fetchall()

        # �������� ��� ������ ���� �������-������
        compare_files(files_in_directory, database_files, subdirectory)

    # ������� ���������� � ����� ������
    conn.close()


def compare_files(files_in_directory, database_files, subdirectory):
    global MY_LOG
    # ����� ���������� �����
    unaccounted_files = set(files_in_directory) - set(file[1] for file in database_files)
    if unaccounted_files:
        my_print(MY_LOG, f"!!! ���������� ����� � �������������: {subdirectory}/{', '.join(unaccounted_files)}")

    else:
        my_print(MY_LOG, f"��� ����� � ������������� {subdirectory} ������")

    # ����� ������������� ������ � ���� ������
    missing_records = set(file[1] for file in database_files) - set(files_in_directory)
    if missing_records:
        my_print(MY_LOG, f"!!! ����������� �����  {subdirectory} / {', '.join(missing_records)} ��� ������� � *.bd")
    else:
        my_print(MY_LOG, f"��� ������ � *.bd ��� ������������� {subdirectory} ����� ��������������� �����")
    my_print(MY_LOG, '----------')











# MY_LOG = "my_log.json"
#
# def my_print(log_file, message):
#     with open(log_file, 'a') as log:
#         log.write(message + '\n')
#
# def compare_torrent_files_with_database(directory_path, database_path):
#     subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
#     conn = sqlite3.connect(database_path)
#     cursor = conn.cursor()
#
#     unaccounted_files_info = []
#     missing_records_info = []
#
#     for subdirectory in subdirectories:
#         subdirectory_path = os.path.join(directory_path, subdirectory)
#         files_in_directory = [f for f in os.listdir(subdirectory_path) if os.path.isfile(os.path.join(subdirectory_path, f))]
#
#         sql_query = f"SELECT path_torrent, torrent FROM torrent WHERE path_torrent = ?"
#         cursor.execute(sql_query, (subdirectory,))
#         database_files = cursor.fetchall()
#
#         unaccounted_files = set(files_in_directory) - set(file[1] for file in database_files)
#         if unaccounted_files:
#             unaccounted_files_info.append({"subdirectory": subdirectory, "files": list(unaccounted_files)})
#
#         missing_records = set(file[1] for file in database_files) - set(files_in_directory)
#         if missing_records:
#             missing_records_info.append({"subdirectory": subdirectory, "files": list(missing_records)})
#
#     conn.close()
#
#     if unaccounted_files_info:
#         my_print(MY_LOG, "!!! ���������� �����:")
#         my_print(MY_LOG, json.dumps(unaccounted_files_info, indent=2))
#         user_choice = input("������� ���������� �����? (y/n): ")
#         if user_choice.lower() == 'y':
#             # �������� ������
#             pass
#
#     if missing_records_info:
#         my_print(MY_LOG, "!!! ������������� ������ � ���� ������:")
#         my_print(MY_LOG, json.dumps(missing_records_info, indent=2))
#         user_choice = input("������� ������������� ������? (y/n): ")
#         if user_choice.lower() == 'y':
#             # �������� ������� � ���� ������
#             pass









if __name__ == "__main__":
    main()
