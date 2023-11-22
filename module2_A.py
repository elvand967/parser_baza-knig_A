# -*- coding: cp1251 -*-
# D:\Python\myProject\parser_baza-knig_A\module2_A.py

'''
В этом модуле загружаем торрент-файлы, имеющиеся на web-страницах
URL которых полученны из book_database.db books (link).
При это загружаем только те торрент-файлы о которых записи в book_database.db torrent (torrent) нет.

Лог-файлы пишем с помощью функции my_print(name_path, text)

'''





import json
import os
import shutil
import sqlite3
import sys
import time
from datetime import datetime
import winreg  # для доступа к реестру Windows при необходимости получения пути к папке загрузки браузеров по умолчанию
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

# Директория в которой размещен исполняемый скрипт 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))

# Путь к папке downloads системы windows получим с помощью нашей функции
download_folder = get_default_download_directory()

# Путь к папке downloads программы, для сортировки и хранения переименованных торрент-файлов
path_dir_downloads_torrent = ''

# Формируем имя лог-файла MY_LOG
now = datetime.now()
script_path = os.path.basename(sys.argv[0])
script_name, _ = os.path.splitext(script_path)
MY_LOG = now.strftime("%Y-%m-%d_%H-%M_") + script_name + ".txt"

def main():
    # определим основные директории
    # Директория в которой размещен исполняемый скрипт 'module2_A.py '
    global path_current_directory

    path_dir_Get = os.path.join(path_current_directory, "JSONfiles\\Get")
    if not os.path.exists(path_dir_Get):
        os.makedirs(path_dir_Get)  # Создаем директорию, если она не существует
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

    # Засекаем начало времени работы кода
    start_time_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time_pars).strftime("%Y.%m.%d %H:%M")

    global script_name
    my_print(MY_LOG, f'{formatted_start_time} Старт скрипта {script_name}')

    # Запускаем меню "Режим работы скрипта"
    menu_mode = menu_script_mode()
    if menu_mode == 1:  # Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"
        # Вызовим меню выбора пакетов загрузки
        path_GetJson_download_package = menu_packages_downloads(path_dir_Get, menu_mode)

        # если функция нам вернула путь к *.json файлу начнем загрузку торрентов
        if path_GetJson_download_package is not None:
            general_functions_torrent(path_GetJson_download_package)

    elif menu_mode == 2:  # 'Режим: "Регистрация загруженных данных в БД"'
        # Вызовим меню выбора пакетов загрузки
        path_SetJson_download_package = menu_packages_downloads(path_dir_Set, menu_mode)

        # если функция нам вернула путь к *.json файлу начнем загрузку в базу данных
        if path_SetJson_download_package is not None:
            # print( f'Команда обновлять БД из {path_SetJson_download_package}')
            general_functions_torrent_db(path_SetJson_download_package)

    elif menu_mode == 3:  # 'Режим: "Сверка загруженных торрент-файлов *.db - Downloads_torrent"'
        downloads_path_torrent = 'Downloads_torrent'
        compare_torrent_files_with_database(downloads_path_torrent, 'book_database.db')


# Меню: режим работы скрипта
def menu_script_mode():
    print('Режимы работы скрипта:\n****************')
    print('  1: Пакеты загрузки (обработка JSON, загрузка торрент файлов)')
    print('  2: Регистрация загруженных данных в БД')
    print('  3: Сверка загруженных торрент-файлов с БД\n****************')
    recd = int(input("Введите № режима работы: "))
    if recd == 1:
        my_print(MY_LOG, 'Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"')
        return 1
    elif recd == 2:
        my_print(MY_LOG, 'Режим: "Регистрация загруженных данных в БД"')
        return 2
    elif recd == 3:
        my_print(MY_LOG, 'Режим: "Сверка загруженных торрент-файлов *.db - Downloads_torrent"')
        return 3


# Функция меню, Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"
def menu_packages_downloads(path_dir, menu_mode):
    while True:
        # Получим список *.json файлов находящихся в принятой директории `path_dir`
        # используя функцию `get_files_in_directory(dir_path)`
        list_json = get_files_in_directory(path_dir, '.json')
        if len(list_json):
            print('\nДоступны JSON-файлы `пакетов загрузки`:\n---------------------')
            # В цикле переберем все JSON-файлы в принятой директории `path_dir`
            for i, file in enumerate(list_json):
                # соберем полный путь к файлу
                file_path = os.path.join(path_dir, file)
                # с помощью функции read_json_file(path_json_download_package)
                # прочтем его, сформировав временный список его словарей
                # что-бы посчитать кол-во этих словарей
                list_dict_json = read_json_file(file_path)
                if len(list_dict_json) == 0:
                    delete_file(path_dir, file)
                    continue
                print(f'  {i} : {file}\t [{len(list_dict_json)}]')
        else:
            print('---------------------\n  Нет доступных JSON-файлов `пакетов загрузки`')

        print('  -------------------')
        if menu_mode == 1:
            print('  N : создать новый `пакет загрузки` (New)')
        print('  X : Выход (Exit)\n---------------------')

        recd = input("Введите индекс `пакета загрузки` или\nбукву для соответствующих действий: ")

        if recd.isdigit():  # если строка состоит из цифр
            i = int(recd)  # приведем к соответсвующемку типу
            if 0 <= i < len(list_json):  # и проверим введен ли корректный (допустимый) индекс
                my_print(MY_LOG, f'\nПакет загрузки: {list_json[i]}')
                # Собираем полный путь к файлу Пакета загрузки
                selected_path_file = os.path.join(path_dir, list_json[i])
                return selected_path_file

        elif recd.isalpha():  # если строка состоит из букв
            if len(recd) == 1:
                if menu_mode == 1 and (recd.upper() == 'N' or recd.upper() == 'Т'):
                    # Запустим функцию создания нового пакета загрузки
                    create_json_with_no_torrent(path_dir)
                    continue
                elif recd.upper() == 'X' or recd.upper() == 'Ч':
                    print('Выход')
                    sys.exit()  # Выходим из программы

        else:
            # если сюда дошли, повторим попытку
            print('Некорректный ввод! Повторите попытку.')


'''Создаем новый `пакет загрузки`'''
def create_json_with_no_torrent(path_dir_Get):
    global path_current_directory
    global MY_LOG

    print('Создаем новый `пакет загрузки`\nУкажите: ' )
    # Запросим аргументы n и x
    n = int(input("начальный id диапозона таблицы `books`: "))
    m = int(input("конечный  id диапозона таблицы `books`: "))
    if m < n:
        m = n

    # Генерируем имя JSON-файла
    file_json_name = f'Get_torrent({n}-{m}).json'

    # Соберем полный путь к "book_database.db"
    name_db = "book_database.db"
    name_db_path = os.path.join(path_current_directory, name_db)

    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect(name_db_path)
    cursor = conn.cursor()

    # Выполняем SQL-запрос для выборки данных

    # cursor.execute(
    #     '''
    #     SELECT books.id, books.title, books.link
    #     FROM books
    #     LEFT JOIN torrent ON books.link = torrent.link
    #     WHERE books.id >= ? AND books.id <= ? AND (torrent.link IS NULL OR torrent.torrent IS NULL OR torrent.torrent = "Null")
    #     ''',
    #     (n, m))


    # Доработан SQL-запрос.
    # Теперь он возращает строки выбранного диапозона для которых
    # нет записей в связанной с books таблице torrent
    # и у которых значение столбца равно "1"
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


    # Извлекаем выбранные строки
    rows = cursor.fetchall()

    # Закрываем соединение
    conn.close()

    # Создаем список словарей на основе выбранных строк
    data = []
    for row in rows:
        id, title, link = row
        data.append({
            "id": id,
            "title": title,
            "link": link,
        })

    # Соберем путь и запишем данные в *.json файл
    file_path = os.path.join(path_dir_Get, file_json_name)
    write_json_file(file_path, data)
    my_print(MY_LOG, f'Создан `пакет загрузки`: {file_json_name}')


''' Общая функция организации загрузки торрент-файлов.
Принимает полный путь к исходному JSON-файлу, формирует список словарей
подлежащий обработке функцией download_torrent_file(page_url) 
по загрузке каждого из торрент-файлов
'''
def general_functions_torrent(path_GetJson_download_package):
    # Получим содержимое исходного JSON-файла в виде списка словарей
    list_dict_json_Get = read_json_file(path_GetJson_download_package)
    # Если не получилось прочитать исходный JSON-файл
    if list_dict_json_Get is None:
        print('Неудачная попытка открыть и прочитать JSON файл.\nВыход')
        sys.exit()  # Выходим из программы

    # Создадим полный путь с именем выходного JSON файла (~Set_torrent(...-...).json)
    # заменив в строке пути и имени файла `Get` на `Set`
    path_SetJson_download_package =remove_replace_substring_postfix(path_GetJson_download_package, 'Get', 'Set')
    # Создадим JSON файл (~Set_torrent(...-...).json) с пустым списком или прочитаем если есть
    list_dict_json_Set = read_json_file(path_SetJson_download_package)

    len_Get_json = len(list_dict_json_Get)
    my_print(MY_LOG, f'Количество элементов в исходном Get~.json: {len_Get_json}')
    my_print(MY_LOG, f'Количество элементов в итоговом Set~.json: {len(list_dict_json_Set)}\n')

    # Засекаем начало времени работы кода
    start_time_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time_pars).strftime("%Y.%m.%d %H:%M")
    my_print(MY_LOG, f'Время начала загрузки торрент-файлов: {formatted_start_time}')

    items_dict = list(list_dict_json_Get)

    # счетчик загруженных торрент-файлов
    sum_torrent = 0

    # Начинаем грузить торрент-файла
    for i, item in enumerate(items_dict):
        # засекаем время обработки URL - словаря страницы
        start_time_URL = time.time()

        page_url = item["link"]
        # Вызываем download_torrent_file для загрузки торрент-файла
        torrent_file = download_torrent_file(page_url)

        my_print(MY_LOG, f'\nЗагрузка торрент-файла №: {i + 1} из {len_Get_json}')
        # print(f'id_db: {item["id"]}, книга `{item["title"]}`.')

        # Фуксируем результат работы функции
        # (имя торрент-файла либо сообщение об ошибке)
        if torrent_file is None:
            end_time_URL = time.time()
            # Посчитаем количество секунд затраченное на обработку URL
            # и с помощью функции format_time(seconds) вернем в формате  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)
            all_time =  format_time(end_time_URL - start_time_pars)

            my_print(MY_LOG,
                     f'!!! Неудачная попытка загрузки торрент-файла,'
                     # f'\nid_db: {item["id"]}, книга `{item["title"]}`.'
                     f'\nВремя обработки URL: {elapsed_time_URL}/{all_time}'
                     f'\nВсего загружено {sum_torrent}/{i + 1}-{len_Get_json}')
            continue
        else:
            # Фуксируем имя загруженного торрент-файла
            item["torrent_old"] = torrent_file

            # Функция переименовывания и сортировки по директориям торрент-файлов
            new_torrent_file = fixing_new_torrent_path(torrent_file, item["id"], item["title"])

            if new_torrent_file is not None:
                item["torrent"] = new_torrent_file["torrent"]
                item["path_torrent"] = new_torrent_file["path_torrent"]

            # При успешной загрузке торрент-файла внесем изменения в списки словарей
            list_dict_json_Set.append(item)  # Добавим новый словарь
            list_dict_json_Get.remove(item)  # Удолим старый словарь

            # Обновляем SetJson-файл
            write_json_file(path_SetJson_download_package, list_dict_json_Set)

            # Обновляем GetJson-файл
            write_json_file(path_GetJson_download_package, list_dict_json_Get)

            # Не забудим посчитать успешную загрузку
            sum_torrent += 1

            end_time_URL = time.time()
            # Посчитаем количество секунд затраченное на обработку URL
            # и с помощью функции format_time(seconds) вернем в формате  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)
            all_time = format_time(end_time_URL - start_time_pars)
            my_print(MY_LOG,
                     # f'Успешно загружен: {torrent_file},\n'
                     # f'книга `{item["title"]}`, id_db: {item["id"]}.\n'
                     f'Время обработки URL: {elapsed_time_URL}/{all_time}\n'
                     f'Всего загружено {sum_torrent}/{i + 1}-{len_Get_json}')

        # Случайная задержка от 1.0 до 1.5 секунд с шагом 0.1 секунд
        random_uni = round(random.uniform(1.0, 1.5), 1)
        time.sleep(random_uni)

    end_time_pars = time.time()
    elapsed_time_pars = end_time_pars - start_time_pars
    elapsed_time_formatted = format_time(elapsed_time_pars)

    my_print(MY_LOG, f"\n\nНа обработку {len_Get_json} элементов, всего затрачено: {elapsed_time_formatted}")
    my_print(MY_LOG, f"Загружено: {sum_torrent} торрент-файлов")
    my_print(MY_LOG, f'\nИтог:'
                     f'\n- в исходном `Get~.json` осталось не обработано элементов: {len(list_dict_json_Get)}')
    my_print(MY_LOG, f'- в итоговом `Set~.json` количество элементов: {len(list_dict_json_Set)}\n\n\n\n')


''' Функция скачивания торрент-файла с URL '''
def download_torrent_file(url):
    try:
        # Путь к папке downloads получим с помощью нашей функции
        global download_folder

        # Получаем список файлов до скачивания в общей папке загрузок браузеров
        filenames_old = set(os.listdir(download_folder))

        # Используем Google Chrome для скачивания торрент-файла
        driver = webdriver.Chrome()

        driver.get(url)  # Открываем страницу

        # wait = WebDriverWait(driver, 60)  # Увеличиваем время ожидания +???
        WebDriverWait(driver, 60)  # Увеличиваем время ожидания +???

        # Используем JavaScript для прокрутки страницы вниз до конца
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Теперь можно продолжить скачивание торрент-файла

        # Проверяем наличие ссылки на торрент
        if driver.find_elements(By.CSS_SELECTOR,
                                "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]"):
            torrent_link_url = driver.find_element(By.CSS_SELECTOR,
                                                   "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]")

            # Кликаем по ссылке торрента
            torrent_link_url.click()

            # wait = WebDriverWait(driver, 60)  # Увеличиваем время ожидания
            WebDriverWait(driver, 60)  # Увеличиваем время ожидания

            # # Подождем 1-2 секунды
            # t1 = random.randint(1, 2)
            # time.sleep(t1)

            #  Попробуем закрыть всплывающее окно, имитация нажатия клавиши "f12"
            pyautogui.press('f12')

            # Подождем еще
            # Случайная задержка от 1.0 до 1.5 секунд с шагом 0.1 секунд
            t2 = round(random.uniform(1.0, 1.5), 1)
            time.sleep(t2)

            # # Дождемся загрузки файла  -???
            # try:
            #     wait.until(lambda x: any(filename.endswith('.torrent') for filename in os.listdir(download_folder)))
            # except TimeoutException:
            #     # print("Торрент-файл не загружен.")
            #     return None

            # Получаем список файлов после скачивания
            filenames_new = set(os.listdir(download_folder))

            # Находим имя нового файла
            downloaded_file = next(iter(filenames_new - filenames_old), None)
            if downloaded_file is not None:
                # Закрываем браузер после скачивания
                driver.quit()
                return downloaded_file

        else:
            my_print(MY_LOG, f"Торрент не найден на странице")
            driver.quit()
            return None

    except Exception as e:
        my_print(MY_LOG, f"Ошибка при скачивании торрент-файла: {e}")
        # driver.quit()
        return None


''' Функция принимает имя загруженного файла и id books
 копирует его в сортировочную директорию и переименовывает.
 возращает словарь с старым, новым именем и путем к нему
 удаляет ранее скаченный файл'''
def fixing_new_torrent_path(torrent_file, id_books, title):
    global download_folder  # Папка загрузки файлов по умолчанию, браузеров системы windows
    global path_dir_downloads_torrent  # Общая папка загрузки файлов скрипта

    # Определим имя сортировачной папки
    subdirectory = str(id_books // 1000)
    # Собираем полный путь к сортировачной папкe
    subdirectory_path = os.path.join(path_dir_downloads_torrent, subdirectory)
    # Проверяем, существует ли указанная директория
    if not os.path.exists(subdirectory_path):
        os.makedirs(subdirectory_path)  # Создаем директорию, если она не существует

    # Определим новое имя торрент-файла
    new_name_torrent_file = f'{clean_filename(title).replace(" ", "_")}_{id_books}.{torrent_file.split(".")[-1]}'

    # Полный путь к исходному торрент-файлу
    source_torrent_file_path = os.path.join(download_folder, torrent_file)

    # Полный путь к новому, переименованному торрент-файлу
    destination_torrent_file_path = os.path.join(subdirectory_path, new_name_torrent_file)

    try:
        # Копируем торрент-файл и переименовываем его
        shutil.copy2(source_torrent_file_path, destination_torrent_file_path)
        my_print(MY_LOG, f'Торрент-файл успешно загружен и переименован:\n`{new_name_torrent_file}`')

        result = {"torrent": new_name_torrent_file,
                  "path_torrent": subdirectory
                  # "path_torrent": destination_torrent_file_path
                  }

        # Вызовим функцию для удаления загруженного файла
        # в папке загрузки файлов по умолчанию, браузеров системы windows
        delete_file(download_folder, torrent_file)

        return result

    except Exception as e:
        print(f'Ошибка при копировании торрент-файла: {e}')
        return None


''' Общая функция фиксации торрент-файлов в БД.
Принимает полный путь к Set JSON-файлу, формирует список словарей
подлежащий обработке функцией ???
'''
def general_functions_torrent_db(path_SetJson_download_package):
    # Получим содержимое исходного JSON-файла в виде списка словарей
    list_dict_json_Set = read_json_file(path_SetJson_download_package)
    # Если не получилось прочитать исходный JSON-файл
    if list_dict_json_Set is None:
        print('Неудачная попытка открыть и прочитать JSON файл.\nВыход')
        sys.exit()  # Выходим из программы
    my_print(MY_LOG, f'Количество словарей в Set~.json: {len(list_dict_json_Set)}\n')

    # Начинаем регестрировать торрент-файлы в БД
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Счетчики
    successful_attempts = 0
    failed_attempts = 0

    for record in list_dict_json_Set:
        link = record.get("link")
        torrent = record.get("torrent")

        # Проверяем наличие записи с таким ключом или торрентом
        cursor.execute('SELECT * FROM torrent WHERE link = ? OR torrent = ?', (link, torrent))
        existing_record = cursor.fetchone()

        if existing_record:
            # Определяем, какое поле вызвало дублирование
            duplicate_field = "link" if existing_record[1] == link else "torrent"
            print(f'Запись с дублирующим значением поля {duplicate_field} ({existing_record[1]})\n'
                  f'уже существует. Пропускаем добавление в таблицу "torrent".\n')
            failed_attempts += 1
            continue
        else:
            # Вставляем новую запись, так как записи с таким ключом не существует
            cursor.execute('''
                INSERT INTO torrent (link, torrent_old, torrent, path_torrent)
                VALUES (?, ?, ?, ?)
            ''', (link, record.get("torrent_old"), torrent, record.get("path_torrent")))
            successful_attempts += 1

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    # Выводим сообщения
    print(f'Успешно добавлено записей в db: {successful_attempts}')
    print(f'Неудачных попыток добавления в db: {failed_attempts}')
    print(f'Всего попыток добавления в db: {successful_attempts + failed_attempts}')


def compare_torrent_files_with_database(directory_path, database_path):
    # Получить список поддиректорий в Downloads_torrent
    subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    # Подключиться к базе данных SQLite
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(directory_path, subdirectory)

        # Получить список файлов в поддиректории
        files_in_directory = [f for f in os.listdir(subdirectory_path) if os.path.isfile(os.path.join(subdirectory_path, f))]

        # SQL-запрос для получения списка имен торрент-файлов для данной поддиректории
        sql_query = f"SELECT path_torrent, torrent FROM torrent WHERE path_torrent = ?"
        cursor.execute(sql_query, (subdirectory,))

        # Получить результат запроса
        database_files = cursor.fetchall()

        # Сравнить два списка имен торрент-файлов
        compare_files(files_in_directory, database_files, subdirectory)

    # Закрыть соединение с базой данных
    conn.close()


def compare_files(files_in_directory, database_files, subdirectory):
    global MY_LOG
    # Найти неучтенные файлы
    unaccounted_files = set(files_in_directory) - set(file[1] for file in database_files)
    if unaccounted_files:
        my_print(MY_LOG, f"!!! Неучтенные файлы в поддиректории: {subdirectory}/{', '.join(unaccounted_files)}")

    else:
        my_print(MY_LOG, f"Все файлы в поддиректории {subdirectory} учтены")

    # Найти отсутствующие записи в базе данных
    missing_records = set(file[1] for file in database_files) - set(files_in_directory)
    if missing_records:
        my_print(MY_LOG, f"!!! Отсутствуют файлы  {subdirectory} / {', '.join(missing_records)} для записей в *.bd")
    else:
        my_print(MY_LOG, f"Все записи в *.bd для поддиректории {subdirectory} имеют соответствующие файлы")
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
#         my_print(MY_LOG, "!!! Неучтенные файлы:")
#         my_print(MY_LOG, json.dumps(unaccounted_files_info, indent=2))
#         user_choice = input("Удалить неучтенные файлы? (y/n): ")
#         if user_choice.lower() == 'y':
#             # Удаление файлов
#             pass
#
#     if missing_records_info:
#         my_print(MY_LOG, "!!! Отсутствующие записи в базе данных:")
#         my_print(MY_LOG, json.dumps(missing_records_info, indent=2))
#         user_choice = input("Удалить отсутствующие записи? (y/n): ")
#         if user_choice.lower() == 'y':
#             # Удаление записей в базе данных
#             pass









if __name__ == "__main__":
    main()
