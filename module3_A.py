# -*- coding: cp1251 -*-
# D:\Python\myProject\parser_baza-knig_A\module3_A.py

'''
Данный модуль парсит страницы "Подробнее" (details)

'''
# import mimetypes
import os
import re
import sqlite3
import sys
import time
import random
# pip install requests
import requests
# pip install requests bs4
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

from utils import clean_filename

# Директория в которой размещен исполняемый скрипт 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))

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


def main():
    menu_mode = menu_script_mode()
    if menu_mode == 1:
        # Список словарей для парсинга
        List_dict_parsing = new_details_parsing_package()
        total_dict = len(List_dict_parsing)
        print( f'Попытка обработать {total_dict} страниц(ы)')
        next_parsing = input('продолжить? ')
        if next_parsing.upper() == 'X' or next_parsing.upper() == 'Ч':
            print('Выход')
            sys.exit()  # Выходим из программы

        ii = 0
        for i, item in enumerate(List_dict_parsing):
            # Запускаем парсер
            parser_total = parser(item["id"], item["title"], item["link"])
            if parser_total is not None:
                # Вносим данные в таблицу  'details'
                insert_details_into_database(parser_total)
                ii += 1
                print(f'успешный парсинг id: {item["id"]} ({ii}/{i + 1}-{total_dict})  {item["title"]}')

            # Случайная задержка от 0.5 до 2 секунд с шагом 0.1 секунд
            delay = round(random.uniform(0.5, 2.0), 1)
            time.sleep(delay)

    elif  menu_mode == 2:
        # Пример использования
        downloads_path = 'Downloads_picture'
        database_path = 'book_database.db'
        compare_files_with_database(downloads_path, database_path)

    else:
        return


def menu_script_mode():
    print('Режимы работы скрипта module3_A.py:\n****************')
    print('  1: Парсинг загрузки ("Подробнее" (details))')
    print('  2: Сверка загруженных картинок с БД\n****************')
    recd = int(input("Введите № режима работы: "))
    if recd == 1:
        print('Режим: Парсинг загрузки ("Подробнее" (details))')
        return 1
    elif recd == 2:
        print('Режим: "Сверка загруженных картинок *.db - Downloads_picture"')
        return 2


'''Создаем новый `пакет парсинга` <details> '''
def new_details_parsing_package():
    global path_current_directory

    print('Создаем новый `пакет парсера`\nУкажите: ' )
    # Запросим аргументы n и x
    n = int(input("начальный id диапозона таблицы `books`: "))
    m = int(input("конечный  id диапозона таблицы `books`: "))
    if m < n:
        m = n

    # Соберем полный путь к "book_database.db"
    name_db = "book_database.db"
    name_db_path = os.path.join(path_current_directory, name_db)

    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect(name_db_path)
    cursor = conn.cursor()

    # Выполняем SQL-запрос для выборки данных
    # books.id, books.title, books.link для строк которых
    # есть записи в таблице `torrent` и отсутствуют записи в таблице `details`
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
        # print(row)

    return data


def key_translation(ru_key):
    translation_dict = {
        'Автор': 'author',
        'Читает': 'reading',
        'Год': 'year',
        'Длительность': 'duration',
        'Качество': 'quality',
        'Цикл': 'cycle',
        'number_cycle': 'number_cycle',
        'Размер': 'size',
        'Жанр': 'genre'
    }
    return translation_dict.get(ru_key, ru_key)


'''
Функция принимает страницы для парсинга и возращает словарь с результатами
'''
def parser(id_books, title, url):
    # Создадим переменную в которой будем хранить адрес сайта, который хотим парсить
    url_base = 'https://baza-knig.ink/'

    # В переменную сохраним юзер-агент, что-бы браузер не считал наши обращения как действия бота
    # HEADERS = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    # }
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0 (Edition Yx 03)'
    }
    # global user_agents

    # отправим запрос на сервер
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            # HEADERS = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=HEADERS, timeout=3)
            response.raise_for_status()  # Проверяем, был ли успешный запрос
            break  # Выход из цикла, если запрос прошел успешно
        except Timeout as e:
            retries += 1
            if retries < max_retries:
                print(f"Ошибка:\n{e}.\n"
                      f"{id_books} {title}: {url}\n"
                      f"Повторная попытка парсинга страницы через 3 секунд (попытка {retries}/{max_retries}).")
                time.sleep(3)
            else:
                print(f"Достигнуто максимальное количество попыток парсинга страницы.\n"
                      f"{id_books} {title}: {url}\n"
                      f"Прекращаем повторные попытки.")
                return None
        except Exception as e:
            print(f"Неожиданная ошибка:\n{e}")
            return None

    soup = BeautifulSoup(response.content, 'html.parser')
    comps = {"id_books": id_books, "link": url}
# -----------------------------------------------
    # Общая информация по книге
    items = soup.find('ul', class_="reset full-items")
    if items:
        li_items = items.find_all('li')

        for li in li_items:
            key = li.contents[0].strip().rstrip(':')

            if key == 'Автор' or key == 'Жанр':
                # Проверяем, что это теги, содержащие несколько значений
                value_list = [a.text.strip() for a in li.find_all('a')]
                comps[key_translation(key)] = ', '.join(value_list)  # Преобразуем список в строку через запятую
                continue

            if key == 'Размер':
                comps['size'] = li.contents[2].text.strip()
                continue
            elif key == 'Цикл':
                comps['cycle'] = li.contents[1].text.strip()

                # Проверяем наличие третьего элемента перед его использованием
                if len(li.contents) > 2:
                    number_cycle_str = li.contents[2].text.strip()
                    match = re.match(r'\((\d+)\)', number_cycle_str)

                    if match:
                        comps['number_cycle'] = int(match.group(1))
                    else:
                        comps['number_cycle'] = None  # Обработка случая, когда не удалось извлечь число
                else:
                    comps['number_cycle'] = None
                continue

            value = li.contents[1].text.strip()
            comps[key_translation(key)] = value

    # -----------------------------------------------
    # Извлекаем описание книги из <div> с классом "short-text"
    description = soup.find('div', class_="short-text").get_text(strip=True)
    if description:
        # Редактируем описание с помощью регулярных выражений Get re
        # Удаление всего, начиная с первого символа "\n" и после
        description = re.sub(r'\n.*', '', description)

        # Удаление всего до "прочти описание:", включая саму фразу.
        description = re.sub(r'^.*?прочти описание:', '', description, flags=re.DOTALL)

        # Удаление всего после "ОзвучкаЕсли в книге говорится"
        description = re.sub(r'ОзвучкаЕсли в книге говорится.*', '', description, flags=re.DOTALL)

        # Удаление пробельных символов и символа перевода строки в начале и конце
        description = description.strip()
        # Добавляем `пару` в словарь
        comps['description'] = description
# -----------------------------------------------
    # Извлекаем данные из тегов - рейтинги
    plot_rating = soup.find('div', {'class': 'multirating-item', 'data-area': 'story'})
    characters_rating = soup.find('div', {'class': 'multirating-item', 'data-area': 'personazh'})
    voice_quality_rating = soup.find('div', {'class': 'multirating-item', 'data-area': 'pisatel'})
    writing_talent_rating = soup.find('div', {'class': 'multirating-item', 'data-area': 'ispolnitel1'})
    final_grade = soup.find('div', {'class': 'multirating-itog'}).find('b', {'class': 'multirating-itog-rateval'})
    like_count = soup.find('div', {'class': 'short-rate'}).find('a', {'title': 'Нравится(+)'}).text.strip()
    dislike_count = soup.find('div', {'class': 'short-rate'}).find('a', {'title': 'Не нравится(-)'}).text.strip()
    comments_count = soup.find('div', {'class': 'comments'}).text.strip()

    # Обновляем словарь comps новыми данными
    comps.update({
            'plot': float(plot_rating.find('canvas').text.strip()),
            'characters': float(characters_rating.find('canvas').text.strip()),
            'voice_quality': float(voice_quality_rating.find('canvas').text.strip()),
            'writing_talent': float(writing_talent_rating.find('canvas').text.strip()),
            'final_grade': float(final_grade.text.strip()),
            'like': int(like_count),
            'dislike': int(dislike_count),
            'comments': int(comments_count)
        })
# -----------------------------------------------
    # Получаем данные для картинки
    img_element = soup.find("div", class_="full-img")
    if img_element and 'src' in img_element.img.attrs:
        img_url = img_element.img['src']
        # img_ext = img_url.split(".")[-1]  # получим расширение картинки

        # Добавляем префикс к URL
        img_url = url_base + img_url

        # Загружаем картинку
        picture = download_image(img_url, id_books, title)
        if picture is not None:
            comps['path_picture'] = picture[0]
            comps['picture'] = picture[1]
        else:
            return None

    return comps


# Функция для загрузки и сохранения картинки
def download_image(url, id_books, title):
    # global user_agents
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0 (Edition Yx 03)'
    }

    # отправим запрос на сервер
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            # HEADERS = {'User-Agent': random.choice(user_agents)}
            response = requests.get(url, headers=HEADERS, timeout=3)
            response.raise_for_status()  # Проверяем, был ли успешный запрос
            break  # Выход из цикла, если запрос прошел успешно
        except Timeout as e:
            retries += 1
            if retries < max_retries:
                print(f"Ошибка:\n{e}.\n"
                      f"{id_books} {title}: {url}\n"
                      f"Повторная попытка загрузки картинки через 3 секунд (попытка {retries}/{max_retries}).")
                time.sleep(3)
            else:
                print(f"Достигнуто максимальное количество попыток загрузки картинки."
                      f"{id_books} {title}: {url}\n"
                      f"\nПрекращаем повторные попытки.")
                return
        except Exception as e:
            print(f"Неожиданная ошибка:\n{e}")
            return

    if response.status_code == 200:
        # Собираем путь к общей папкe картинок
        path_shared_images_folder = os.path.join(path_current_directory, "Downloads_picture")
        if not os.path.exists(path_shared_images_folder):
            os.makedirs(path_shared_images_folder)  # Создаем директорию, если она не существует

        # Определим имя сортировачной папки
        path_picture = str(id_books // 1000)

        # Полный путь к сортировачной папке
        download_dir = os.path.join(path_shared_images_folder, path_picture)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)  # Создаем директорию, если она не существует

        # Определим новое имя изображения
        img_ext = url.split(".")[-1]  # получим расширение картинки из url
        filename = f'{clean_filename(title).replace(" ", "_")}_{id_books}.{img_ext}'
        filepath = os.path.join(download_dir, filename)

        # Сохраняем картинку
        with open(filepath, 'wb') as f:
            f.write(response.content)
        return [path_picture, filename]

    else:
        print(f"Не удалось загрузить картинку. Код статуса: {response.status_code}")
        return None


# Фиксация данных в таблице 'details'
def insert_details_into_database(details_dict):
    # Подключаемся к базе данных
    conn = sqlite3.connect('book_database.db')
    cursor = conn.cursor()

    # Список требуемых ключей
    required_keys = [
        'id_books', 'link', 'author', 'reading', 'year', 'duration', 'quality', 'cycle', 'number_cycle',
        'size', 'genre', 'description', 'picture', 'path_picture', 'plot', 'writing_talent',
        'characters', 'voice_quality', 'final_grade', 'like', 'dislike', 'comments'
    ]

    # Генерируем SQL-запрос для вставки данных
    sql_query = '''
        INSERT INTO details (
            {}
        )
        VALUES ({})
    '''.format(', '.join(required_keys), ', '.join(['?'] * len(required_keys)))

    # Извлекаем значения из словаря
    values = tuple(details_dict.get(key, None) for key in required_keys)

    # Выполняем запрос
    cursor.execute(sql_query, values)

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


def compare_files_with_database(directory_path, database_path):
    # Получить список поддиректорий в Downloads_picture
    subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]

    # Подключиться к базе данных SQLite
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    print('==========')
    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(directory_path, subdirectory)

        # Получить список файлов в поддиректории
        files_in_directory = [f for f in os.listdir(subdirectory_path) if os.path.isfile(os.path.join(subdirectory_path, f))]

        # SQL-запрос для получения списка имен файлов для данной поддиректории
        sql_query = f"SELECT path_picture, picture FROM details WHERE path_picture = ?"
        cursor.execute(sql_query, (subdirectory,))

        # Получить результат запроса
        database_files = cursor.fetchall()

        # Сравнить два списка имен файлов
        compare_files(files_in_directory, database_files, subdirectory)

    # Закрыть соединение с базой данных
    conn.close()

def compare_files(files_in_directory, database_files, subdirectory):
    # Найти неучтенные файлы
    unaccounted_files = set(files_in_directory) - set(file[1] for file in database_files)
    if unaccounted_files:
        print(f"!!! Неучтенные файлы в поддиректории: {subdirectory}/{', '.join(unaccounted_files)}")
    else:
        print(f"Все файлы в поддиректории {subdirectory} учтены")

    # Найти отсутствующие записи в базе данных
    missing_records = set(file[1] for file in database_files) - set(files_in_directory)
    if missing_records:
        print(f"!!! Отсутствуют файлы  {subdirectory} / {', '.join(missing_records)} для записей в *.bd")
    else:
        print(f"Все записи в *.bd для поддиректории {subdirectory} имеют соответствующие файлы")
    print('----------')









if __name__ == "__main__":
    main()