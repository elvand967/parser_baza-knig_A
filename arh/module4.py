# D:\Python\myProject\parser_baza-knig\module4.py

'''
В этом модуле попытаемся повторно загрузить торрент-файлы, что не получилось ранее
1

Готовим *.json к формированию БД.


Анализируем результаты работы module2.py и формируем 2 *.json файла:
1) book_database_total.json (полный комплект данных)
2) book_database3.json (словари требующие дозагрузки только торрентов)

Источник  *.json вводим в ручном режиме выбором из доступных файлов по индексу

Как выяснелось, кроме неполного скачивания торрент-файлов, наш модуль module2.py
так-же не мало накосячил и пропустил некоторые ссылки
Еще возникает вопрос о скаченных картинка? К нему вернемся позже!!!
'''

import os
import json
import random
import time
from itertools import islice

import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

total_tjrrent = 0

def main():
    # Путь к директории результатов анализа
    dirJSONtotal = "JSONtotal"

    # Источник словарей (ссылок)
    source_json = 'book_database3.json'

    # Сохраняем результат обработки
    result_json = 'book_database_total.json'

    # Проверяем, существует ли "JSONtotal" - директория, для сохранения результатов,
    # и создаем её, если она не существует
    if not os.path.exists(dirJSONtotal):
        os.makedirs(dirJSONtotal)
        print(f'Требуемая директория {dirJSONtotal}, была вновь создада.\n JSON-файлы отсутствуют.\n Работа кода остановлена')
        return

    # Собираем полный путь к исходному JSON-файлу "source_json"
    file_path3 = os.path.join(dirJSONtotal, source_json)
    # Получим содержимое исходного JSON-файла в виде списка словарей
    json_files_notTorrent = read_json_file(file_path3)
    print(f'Количество элементов в {source_json}: [{len(json_files_notTorrent)}]')

    # Собираем полный путь к итоговому JSON-файлу "result_json"
    file_path_total = os.path.join(dirJSONtotal, result_json)
    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_total = read_json_file(file_path_total)
    print(f'Количество элементов в {result_json}: [{len(json_files_total)}]')

    # Зададим диапозон обрабатываемых элементов списка
    # от 'start_index' до 'end_index' включая границы
    start_index = int(input("Первый индекс при старте: "))
    end_index = int(input("Индекс на финише: "))
    if end_index < start_index:
        end_index = start_index

    # Выберем интересующий нас диапозон списка
    filtered_items = islice(json_files_notTorrent, start_index, end_index+1)

    # Засекаем начало времени работы кода
    start_time_pars = time.time()

    print(f'Старт загрузки торрент-файлов.\nДиапозона словарей от {start_index} до {end_index} (включительно).\n' )

    for i, item in enumerate(filtered_items):
        page_url = item["link"]
        # Вызываем download_torrent_file для сохранения торрент-файла
        torrent_file = download_torrent_file(page_url)
        item["torrent"] = torrent_file
        if torrent_file == "Ошибка" or torrent_file == None:
            continue
        else:
            json_files_total.append(item)
            json_files_notTorrent.remove(item)
            print(f'Для индекса: {source_json}_[{i}] - id: {item["id"]}\nУспешно загружен: {torrent_file}')

            # Обновляем JSON-файлу "book_database_total.json"
            write_json_file(file_path_total, json_files_total)

            # Обновляем JSON-файл "book_database3.json"
            write_json_file(file_path3, json_files_notTorrent)
            print('-----------')

    end_time_pars = time.time()
    elapsed_time_pars = end_time_pars - start_time_pars
    elapsed_time_formatted = format_time(elapsed_time_pars)

    print(f"\nНа обработку {end_index-start_index+1} элементов, всего затрачено время : {elapsed_time_formatted}")
    print(f"Загружено: {end_index-start_index+1} торрент-файлов")

def download_torrent_file(url):
    global total_tjrrent
    try:
        download_folder = "D:\\User\\Downloads"  # Путь к папке downloads

        # Получаем список файлов до скачивания в общей папке загрузок браузеров
        filenames_old = set(os.listdir(download_folder))

        # Используем Google Chrome для скачивания торрент-файла
        driver = webdriver.Chrome()

        driver.get(url)  # Открываем страницу

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

            wait = WebDriverWait(driver, 60)  # Увеличиваем время ожидания

            # Подождем 1-2 секунды
            t1 = random.randint(1, 2)
            time.sleep(t1)

            #  Попробуем закрыть всплывающее окно, если оно есть.
            #  Имитация нажатия клавиши "f12"
            pyautogui.press('f12')

            # Подождем еще 2-3 секунды
            t2 = random.randint(2, 3)
            time.sleep(t2)

            # Дождемся загрузки файла
            try:
                wait.until(lambda x: any(filename.endswith('.torrent') for filename in os.listdir(download_folder)))
            except TimeoutException:
                print("Торрент-файл не загружен.")
                return None

            # Получаем список файлов после скачивания
            filenames_new = set(os.listdir(download_folder))

            # Находим имя нового файла
            downloaded_file = next(iter(filenames_new - filenames_old), None)
            if downloaded_file is not None:
                total_tjrrent = total_tjrrent+1
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


'''
Функция read_json_file(file_path) попытается открыть и прочитать JSON файл по указанному пути 
и вернет его содержимое в виде словаря. 
Если файл не будет найден Функция создаст его,
Если произойдет ошибка при декодировании JSON - функция вернет None.
'''
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Файл {file_path} - не найден.\nСоздан новый файл {file_path}.")
        data = []
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return data
    except json.JSONDecodeError:
        print(f"Ошибка при декодировании JSON файла: {file_path}")
        return None


'''
Функция 'write_json_file(file_path, data)' принимает путь к JSON файлу 
и список словарей (или других объектов, которые могут быть сериализованы в JSON) 
и записывает их в указанный файл. 
Если файл существует, он будет перезаписан новыми данными.
'''
def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    # print(f"Данные успешно записаны в файл: {file_path}")


# функция format_time преобразует количество секунд в формат "hh:mm:ss"
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


if __name__ == "__main__":
        main()