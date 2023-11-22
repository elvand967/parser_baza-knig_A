# -*- coding: cp1251 -*-

# D:\Python\myProject\parser_baza-knig_A\utils.py
import shutil
import sqlite3
import json
import os
import winreg  # ��� ������� � ������� Windows ��� ������������� ��������� ���� � ����� �������� ��������� �� ���������
from datetime import datetime
import unicodedata
# from setuptools.msvc import winreg



''' ������� �������� � ������ ������ ���������� � ���� ���������
� ������ � ��� ������������ ��� ��������� � ��������� �����'''
def my_print(name_path, text):
    # ��������� ������� ����� �� ��������� ����
    if os.path.exists(name_path):
        # ��������� ���� ��� ���������� ������
        with open(name_path, "a", encoding="utf-8") as file:
            # ��������� ���������� ����� � ����� ������
            file.write("\n" + text)
    else:
        # ������� ����� ���� � ���������� �����
        with open(name_path, "w", encoding="utf-8") as file:
            file.write(text)
    # ������� ����� � ��������
    print(text)


'''
������� ������� ����� ���������� ���� � ���������� Downloads 
������������� �������� ������� ��� ���������� ������ �� ��������� 
�� ��������� ��� ��������� (D:\\User\\Downloads).
��� ��������� ��������������� ���� � ������� � �������� �������� ���� � ���������� Downloads. 
����� �� ���������, ���������� �� ��������� ����������. 
'''
def get_default_download_directory():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{374DE290-123F-4565-9164-39C4925E467B}"

    try:
        # ��������� ��������������� ���� � �������
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # �������� �������� ���� � ���������� Downloads
            download_path, _ = winreg.QueryValueEx(key, value_name)

            # ����������� � ���������� ����
            download_path = os.path.expanduser(download_path)

            # ���������� ������� ��������� �����
            download_path = download_path.replace("\\", "\\\\")

            # ���������, ���������� �� ����������
            if os.path.exists(download_path):
                return download_path
            else:
                print(f"The directory '{download_path}' does not exist.")
                return None

    except Exception as e:
        print(f"Error accessing the registry: {e}")
        return None


''' ������� ������� �������������� �������� � ��������'''
# def transliterate(text):
#     translit_dict = {
#         '�': 'a', '�': 'b', '�': 'v', '�': 'g', '�': 'd', '�': 'e', '�': 'e',
#         '�': 'zh', '�': 'z', '�': 'i', '�': 'y', '�': 'k', '�': 'l', '�': 'm',
#         '�': 'n', '�': 'o', '�': 'p', '�': 'r', '�': 's', '�': 't', '�': 'u',
#         '�': 'f', '�': 'kh', '�': 'ts', '�': 'ch', '�': 'sh', '�': 'shch',
#         '�': '', '�': 'y', '�': '', '�': 'e', '�': 'yu', '�': 'ya'
#     }
#
#     result = []
#     for char in text:
#         lower_char = char.lower()
#         result.append(translit_dict.get(lower_char, char))
#
#     return ''.join(result)
def transliterate(text):
    translit_dict = {
        '�': 'a', '�': 'b', '�': 'v', '�': 'g', '�': 'd', '�': 'e', '�': 'e',
        '�': 'zh', '�': 'z', '�': 'i', '�': 'y', '�': 'k', '�': 'l', '�': 'm',
        '�': 'n', '�': 'o', '�': 'p', '�': 'r', '�': 's', '�': 't', '�': 'u',
        '�': 'f', '�': 'kh', '�': 'ts', '�': 'ch', '�': 'sh', '�': 'shch',
        '�': '', '�': 'y', '�': '', '�': 'e', '�': 'yu', '�': 'ya'
    }

    result = []
    for char in text:
        normalized_char = unicodedata.normalize('NFKD', char)
        result.append(translit_dict.get(normalized_char.lower(), char))

    return ''.join(result)


'''������� ��� ������� ����� ����� �� ����������� �������� 
� � ������� ������� transliterate(text) ������������ �������������� (ru-en).
������� ������������ ������� �� ������.
������� ����� �� ������ �������������.
������ ������������� ������.
������ ������������� ������ ������������� � ����� �����
'''
def clean_filename(filename):
    # ������ ������������ �������� �� �����
    invalid_chars = {'/', '\\', ':', '*', '?', '"', '<', '>', '|'}
    filename = ''.join('-' if c in invalid_chars else c for c in filename)

    # ������ ����� �� ������ �������������
    filename = filename.replace('.', '_')

    # �������� ������������� �������
    filename = '-'.join(filter(None, filename.split('-')))

    # �������� ������������� ������ �������������
    filename = '_'.join(filter(None, filename.split('_')))

    return transliterate(filename)


''' ������� read_json_file(path_json_download_package) ���������� 
������� � ��������� JSON ���� �� ���������� ����
� ������� ��� ���������� � ���� ������ ��������.
���� ����� ���, �������� ��� � ������ �������'''
def read_json_file(path_json_download_package):
    try:
        with open(path_json_download_package, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # print(f"���� {path_json_download_package} - �� ������.\n������ ����� ���� {file_path}.")
        data = []
        with open(path_json_download_package, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return data
    except json.JSONDecodeError:
        print(f"������ ��� ������������� JSON �����: {path_json_download_package}")
        return None


''' ������� ��������� ���� � ���������� � ���������� �����,
���������� ������ ��������� � ��� ������ � ��������� �����������
� ������ ������ ��������� ������ ������ � ��������� � ������ '''
def get_files_in_directory(dir_path, file_extension='.json'):
    try:
        file_list = [file for file in os.listdir(dir_path) if file.endswith(file_extension) and os.path.isfile(os.path.join(dir_path, file))]
        return file_list
    except Exception as e:
        print(f"An error occurred/��������� ������:\n{e}")
        return []


''' ������� �������� ����� '''
def delete_file(file_path, file_name):
    # ��������� ������ ���� � �����
    full_path = os.path.join(file_path, file_name)

    try:
        # ������� ����
        os.remove(full_path)
        print(f'���� `{file_name}` ������� ������.')
    except FileNotFoundError:
        print(f'���� {full_path} �� ������.')
    except PermissionError:
        print(f'����������� ����� �� �������� ����� {full_path}.')
    except Exception as e:
        print(f'��������� ������ ��� �������� ����� {full_path}: {e}')


''' ������� �������� ����� ����/����� ������ ��� ��������� ��������� � ����� ������  '''
def remove_replace_substring_postfix(path_file_name, substring, new_substring=''):
    if substring is not None:
        # �������� ��� ������� ����������� ���������
        new_path_file_name = path_file_name.replace(substring, new_substring)
        # ������� ���/���� � ������������ ����������
        return new_path_file_name
    else:
        # ���� `substring` ����� None, �������� new_substring ����� ������ (����������� �����)
        base_path, extension = os.path.splitext(path_file_name)
        return base_path + new_substring + extension


''' ������� format_time(seconds) ����������� ���������� ������ � ������ "hh �. mm �. ss �." '''
def format_time(seconds):
    if seconds >= 60:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}."
    else:
        return f"{int(seconds):02d} ���."


''' ������� 'write_json_file(file_path, data)' ��������� ����������, ���� � JSON �����
� ������ �������� (��� ������ ��������, ������� ����� ���� ������������� � JSON)
���������� ������ (data) � ��������� ����.
���� ���� ����������, �� ����� ����������� ������ �������.   '''
def write_json_file(path_file_name, data):
    with open(path_file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


#++++++++++++++++++++++++++++++++++++++++++++++++++
def create_backup(db_file, backup_folder='backup'):
    # ������� ����� ��� �������� ��������� �����, ���� � ���
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # ������������ ��� ��������� ����� � �������������� ���� � �������
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'{backup_folder}/book_database_backup_{timestamp}.db'

    try:
        # ������� ��������� �����
        shutil.copy(db_file, backup_file)
        print(f'��������� ����� �������: {backup_file}')
    except Exception as e:
        print(f'������ ��� �������� ��������� �����: {e}')

# ����� ������� ��� �������� ��������� ����� ��
# create_backup("D:\\Python\\myProject\\parser_baza-knig_A\\book_database.db", 'backup')
#++++++++++++++++++++++++++++++++++++++++++++++++++


''' ������� `def compare_database_and_files(database_path, downloads_path)`
������: �������� ������ ������������ ������ ��������������� � ������� "torrent" � ���������� ���������� ������� � ��������������� ���������
������� ����� � ������� � ������� "torrent" ��� ������� ���������� ��� ������ � ��������� �����,
� ���-�� ����� � ������ ������� �� ������ � ������� "torrent".
���� ������-���� ������������� �� ����� ��������, ���-�� ������������� �� ����.
'''
def compare_database_and_files(database_path, downloads_path):
    try:
        # ����������� � ���� ������
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # ��������� ������ ������� �� ������� "torrent"
        cursor.execute('SELECT link, torrent, path_torrent FROM torrent')
        db_records = cursor.fetchall()

        # ��������� ������ ������ �� �����
        file_records = []
        for path_torrent, _, filenames in os.walk(downloads_path):
            for filename in filenames:
                file_records.append((os.path.join(path_torrent, filename), filename, os.path.relpath(path_torrent, downloads_path)))

        # ��������� ������� � ���� ������ � ������ �� �����
        missing_files_db = [record for record in db_records if record[2] not in [file_record[2] for file_record in file_records]]
        missing_files_disk = [file_record for file_record in file_records if (file_record[2], file_record[1]) not in [(record[2], record[1]) for record in db_records]]

        # ����� ������
        if missing_files_db:
            print("������ � ���� ������ ��� ������ �� �����:")
            for link, torrent, path_torrent in missing_files_db:
                print(f"Link: {link}, Torrent: {torrent}, Path_torrent: {path_torrent}")

        if missing_files_disk:
            print("����� �� ����� ��� ������� � ���� ������:")
            for file_path, filename, path_torrent in missing_files_disk:
                print(f"File path: {file_path}, Filename: {filename}, Path_torrent: {path_torrent}")

        if not missing_files_db and not missing_files_disk:
            print("�������������� ����� ����� ������ � ������� �� ����� �� ��������.")

    except Exception as e:
        print(f"��������� ������: {e}")

    finally:
        # �������� ����������
        if conn:
            conn.close()

# ����� `def compare_database_and_files(database_path, downloads_path)`
# compare_database_and_files("book_database.db", "D:\\Python\\myProject\\parser_baza-knig_A\\Downloads_torrent")
#++++++++++++++++++++++++++++++++++++++++++++++++++




