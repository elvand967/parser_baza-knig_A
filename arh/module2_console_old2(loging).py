# D:\Python\myProject\parser_baza-knig\module2.py
import mimetypes
import sys
import time
import random
import os
import re
import json
import requests
from bs4 import BeautifulSoup
import datetime
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from transliterate import translit
from module1 import URL, HEADERS


# Функция для загрузки данных из JSON
def load_data_from_json(file_path, n, x):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Отфильтруем словари, оставив только те, где "id" в диапазоне от n до x
    filtered_data = [item for item in data if x >= item['id'] >= n]

    return filtered_data


# Определите новую функцию parser_description
def parser_description(soup):

    data = {}

    # Извлекаем данные из <ul> с классом "full-items"
    ul_tag = soup.find('ul', class_='full-items')
    if ul_tag:
        list_items = ul_tag.find_all('li')

        for item in list_items:
            text = item.get_text(strip=True)
            key, value = text.split(':', 1)

            # Транслитерация ключа
            key = translit(key.strip(), reversed=True)
            key = key.lower().replace(' ', '_')

            value = value.strip()
            data[key] = value

    # Извлекаем текст из <div> с классом "short-text"
    div_short_text = soup.find('div', class_='short-text')
    if div_short_text:
        description = div_short_text.get_text()

        # Редактируем описание с помощью регулярных выражений import re
        # Удаление всего, начиная с первого символа "\n" и после
        description = re.sub(r'\n.*', '', description)

        # Удаление всего до "прочти описание:", включая саму фразу.
        description = re.sub(r'^.*?прочти описание:', '', description, flags=re.DOTALL)

        # Удаление пробельных символов и символа перевода строки в начале и конце
        description = description.strip()

        data['description'] = description

    return data


def download_torrent_file(url):
    try:
        # Используем Firefox для скачивания торрент-файла
        driver = webdriver.Firefox()

        download_folder = "D:\\User\\Downloads"  # Путь к папке downloads

        # Получаем список файлов до скачивания
        filenames_old = set(os.listdir(download_folder))

        driver.get(url)  # Открываем страницу
        # Проверяем наличие ссылки на торрент
        if driver.find_elements(By.CSS_SELECTOR,
                                "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]"):
            torrent_link_url = driver.find_element(By.CSS_SELECTOR,
                                                   "a[onclick=\"yaCounter46924785.reachGoal('clickTorrent'); return true;\"]")

            # Кликаем по ссылке торрента
            torrent_link_url.click()

            wait = WebDriverWait(driver, 600)  # Увеличиваем время ожидания

            # Дождемся загрузки файла
            try:
                wait.until(lambda x: any(filename.endswith('.torrent') for filename in os.listdir(download_folder)))
            except TimeoutException:
                print("Торрент-файл не загружен.")
                return None

            # Получаем список файлов после скачивания
            filenames_new = set(os.listdir(download_folder))

            # Находим имя нового файла
            downloaded_file = (filenames_new - filenames_old).pop()

            # Закрываем браузер после скачивания
            driver.quit()

            return downloaded_file

        else:
            print(f"Торрент не найден на странице")
            driver.quit()
            return "Торрент не найден"

    except Exception as e:
        print(f"Ошибка при скачивании торрент-файла: {e}")
        driver.quit()
        return "Ошибка"


def parser_page(dict_page, URL = URL, HEADERS = HEADERS):
    # Извлекаем URL страницы из словаря
    page_url = dict_page.get("link")

    if page_url:
        try:
            # Делаем GET-запрос к странице
            response = requests.get(page_url, headers=HEADERS)
            response.raise_for_status()  # Проверяем успешность запроса

            # Создаем объект BeautifulSoup для парсинга страницы
            soup = BeautifulSoup(response.text, "html.parser")

            # Вызываем parser_description для извлечения данных
            description_data = parser_description(soup)

            # Вызываем download_torrent_file для сохранения торрент-файла
            torrent_file = download_torrent_file(page_url)

            # Извлекаем URL картинки
            img_element = soup.find("div", class_="full-img").find("img")
            img_src = img_element.get("src")

            if img_src:
                # Добавляем префикс URL сайта, если необходимо
                if not img_src.startswith("http"):
                    img_src = f"{URL}/{img_src}"

                # Получаем имя файла из URL
                img_filename = os.path.basename(img_src)
                img_save_path = os.path.join("img_downloads", img_filename)

                # Создаем директорию, если она не существует
                # os.makedirs("img_downloads", exist_ok=True)
                os.makedirs("D:\Python\myProject\parser_baza-knig\img_downloads", exist_ok=True)

                # Скачиваем и сохраняем изображение
                response = requests.get(img_src, headers=HEADERS)
                response.raise_for_status()

                # Получим исходное расширение изображения
                content_type = response.headers.get('content-type')
                if content_type:
                    ext = mimetypes.guess_extension(content_type)
                    if ext:
                        ext = ext.lstrip('.')
                    else:
                        ext = "jpg"
                else:
                    ext = "jpg"

                # Вызываем функцию для переименования изображения
                img_filename = rename_and_save_image(dict_page['title'], ext)

                # Сохранение изображения
                # img_save_path = os.path.join("img_downloads", img_filename)
                img_save_path = os.path.join("D:\Python\myProject\parser_baza-knig\img_downloads", img_filename)
                with open(img_save_path, "wb") as img_file:
                    img_file.write(response.content)

                # Обновляем словарь dict_page_new
                dict_page_new = dict(dict_page, **description_data)
                dict_page_new["image_file"] = img_filename
                dict_page_new["torrent"] = torrent_file

                # Вызываем функцию для сохранения данных в JSON
                save_to_json(dict_page_new, "D:\Python\myProject\parser_baza-knig\\book_database2.json")

            else:
                print("Изображение не найдено на странице.")

        except Exception as e:
            print(f"Ошибка при парсинге страницы {page_url}: {e}")
    else:
        print("URL страницы отсутствует в словаре.")


def rename_and_save_image(title, ext):

    # Замена пробелов и недопустимых символов на нижнее подчеркивание
    character_control = re.sub(r'[^\w-]', '_', title)  # Заменяем пробелы, символы исключая буквы, цифры, дефис и подчеркивание

    # Проверяем, есть ли хотя бы одна буква
    if any(c.isalpha() for c in character_control):
        # Если есть буквы, транслируем
        latin_title = translit(character_control, reversed=True)
    else:
        # Если нет букв, просто добавляем префикс "f_"
        latin_title = f"f_{character_control}"

    # Заменяем пробелы на нижнее подчеркивание
    sanitized_title = re.sub(r'[\s]+', '_', latin_title)

    # Получение текущей даты в формате "MMDDSS"
    current_date = datetime.datetime.now().strftime("%m%d%S")

    # Формирование имени файла изображения
    img_filename = f"{sanitized_title}_{current_date}.{ext}"

    return img_filename


# Эта функция создает JSON-файл и добавляет данные в 'book_database2.json'
def save_to_json(data, file_path):
    # Проверяем существование файла
    if os.path.exists(file_path):
        # Если файл существует, загружаем его содержимое
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)
    else:
        # Если файла нет, создаем пустой список
        existing_data = []

    # Добавляем новые данные к существующим данным
    existing_data.append(data)

    # Сохраняем обновленные данные в файл
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)

# функция format_time преобразует количество секунд в формат "hh:mm:ss"
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"



# Функция main принимает список словарей с данными, в том числе url страниц, парсинг которых нужно произвести
def main(n, x):
    # Генерируем уникальное имя для лог-файла
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"D:\Python\myProject\parser_baza-knig\log_{current_time}_n{n}_x{x}.txt"

    # Настройка логгера
    logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(message)s")

    # Открываем лог-файл для записи
    logging.info(f"Лог-файл для n={n} и x={x}")

    # Определяем путь к исходному '*.json'
    file_path = 'D:\Python\myProject\parser_baza-knig\\book_database.json'

    # Вызываем функцию для загрузки данных из JSON
    data = load_data_from_json(file_path, n, x)

    logging.info("Загружены данные из JSON.")

    # Засекаем начало времени работы кода
    start_time_pars = time.time()

    # Запускаем цикл по словарям
    for dict_page in data:
        logging.info(f"\nid: {dict_page['id']}\nПарсинг страницы: {dict_page['title']}")

        # Засекаем начало времени
        start_time = time.time()

        parser_page(dict_page)

        # Засекаем конец времени и рассчитываем время
        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info(f"Время парсинга страницы: {elapsed_time:.2f} сек")
        t = random.randint(1, 3)
        logging.info(f'Задержка {t} seconds')

        time.sleep(t)

    end_time_pars = time.time()
    elapsed_time_pars = end_time_pars - start_time_pars
    elapsed_time_formatted = format_time(elapsed_time_pars)

    logging.info(f"\nВсего затрачено время на парсинг: {elapsed_time_formatted}")

if __name__ == "__main__":
    # Проверим, переданы ли аргументы командной строки
    if len(sys.argv) == 3:
        # Получим значения n и x из аргументов командной строки
        n = int(sys.argv[1])
        x = int(sys.argv[2])
        if x < n:
            x = n
        main(n, x)
    else:
        # Запросим аргументы n и x
        n = int(input("№ id при старте: "))
        x = int(input("№ id на финише: "))
        if x < n:
            x = n
        main(n, x)
