# D:\Python\myProject\parser_baza-knig_A\module3_A.py

'''
Данный модуль парсит страницы "Подробнее" (details)

'''
import mimetypes
import os
import re
import sqlite3
import time
import random
# pip install requests
import requests
# pip install requests bs4
from bs4 import BeautifulSoup

from utils import write_json_file, clean_filename

# Директория в которой размещен исполняемый скрипт 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))

def main():
    # Список словарей для парсинга
    List_dict_parsing = new_details_parsing_package()

    for item in List_dict_parsing:
        # print(item["link"])
        parser(item["id"], item["title"], item["link"])
        # Случайная задержка от 0.5 до 2 секунд с шагом 0.1 секунд
        delay = round(random.uniform(0.5, 2.0), 1)
        time.sleep(delay)


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
    return data


def key_translation(ru_key):
    translation_dict = {
        'Автор': 'author',
        'Читает': 'reading',
        'Год': 'year',
        'Длительность': 'duration',
        'Качество': 'quality',
        'Цикл': 'cycle',
        'Размер': 'size',
        'Жанр': 'genre'
    }
    return translation_dict.get(ru_key, ru_key)


def save(comps):
    with open('pars01_info.txt', 'a') as file:
        for comp in comps:
            file.write(f"{comp['title']}\nОписание: {comp['text']}\nСсылка: {comp['link']}\n\n")


'''
Функция принимает страницы для парсинга и возращает словарь с результатами
'''
def parser(id_books, title, URL):
    # Создадим переменную в которой будем хранить адрес сайта, который хотим парсить
    # URL = 'https://baza-knig.ink/'

    # В переменную сохраним юзер-агент, что-бы браузер не считал наши обращения как действия бота
    # HEADERS = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    # }
    HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 OPR/100.0.0.0 (Edition Yx 03)'
    }

    # отправим запрос на сервер
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    comps = {}
# -----------------------------------------------
    # Общая информация по книге
    items = soup.find('ul', class_="reset full-items")
    if items:
        li_items = items.find_all('li')
        for li in li_items:
            key = li.contents[0].strip().rstrip(':')
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

        # Удаление пробельных символов и символа перевода строки в начале и конце
        description = description.strip()
        # Добавляем `пару` в словарь
        comps['description'] = description
# -----------------------------------------------
        # Получаем данные для картинки
        img_element = soup.find("div", class_="full-img")
        if img_element and 'src' in img_element.img.attrs:
            img_url = img_element.img['src']
            # img_ext = img_url.split(".")[-1]  # получим расширение картинки

            # Добавляем префикс к URL
            img_url = "https://baza-knig.ink" + img_url

            # Загружаем картинку
            picture = download_image(img_url, id_books, title)
            if picture is not None:
                comps['path_picture'] = picture[0]
                comps['picture'] = picture[1]

    print(comps)

# Функция для загрузки и сохранения картинки
def download_image(url, id_books, title):
    response = requests.get(url)
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


if __name__ == "__main__":
    main()
