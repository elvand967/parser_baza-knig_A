# D:\Python\myProject\parser_baza-knig\module4.py

'''
В этом модуле попытаемся повторно загрузить торрент-файлы, что не получилось ранее


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
import time
from itertools import islice

from selenium import webdriver

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main(start_index, end_index):
    # Путь к директории результатов анализа
    dirJSONtotal = "JSONtotal"

    # Проверяем, существует ли "JSONtotal" - директория, для сохранения результатов,
    # и создаем её, если она не существует
    if not os.path.exists(dirJSONtotal):
        os.makedirs(dirJSONtotal)
        return

    # Собираем полный путь к итоговому JSON-файлу "book_database3.json"
    file_path3 = os.path.join(dirJSONtotal, 'book_database3.json')
    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_notTorrent = read_json_file(file_path3)
    print(f'Количество элементов в {file_path3} равно: {len(json_files_notTorrent)}')

    # Собираем полный путь к итоговому JSON-файлу "book_database_total.json"
    file_path_total = os.path.join(dirJSONtotal, 'book_database_total.json')
    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_total = read_json_file(file_path_total)
    print(f'Количество элементов в {file_path_total} равно: {len(json_files_total)}')

    filtered_items = islice(json_files_notTorrent, start_index, end_index+1)

    print(f'Старт загрузки торрент-файлов;\nДиапозона словарей от {start_index} до {end_index} (включительно)\n' )

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
            print(f'Для индекса: {i} - id: {item["id"]}\nУспешно загружен: {torrent_file}\n-----------')

            # Обновляем JSON-файлу "book_database_total.json"
            write_json_file(file_path_total, json_files_total)

            # Обновляем JSON-файл "book_database3.json"
            write_json_file(file_path3, json_files_notTorrent)
            print('-----------')



def download_torrent_file(url):
    try:
        download_folder = "D:\\User\\Downloads"  # Путь к папке downloads

        # Получаем список файлов до скачивания в общей папке загрузок браузеров
        filenames_old = set(os.listdir(download_folder))

        # Используем Firefox для скачивания торрент-файла
        options = webdriver.FirefoxOptions()
        options.headless = True

        driver = webdriver.Firefox(options=options)
        # Устанавливаем размер окна (ширина x высота)
        driver.set_window_size(360, 740)

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

            wait = WebDriverWait(driver, 600)  # Увеличиваем время ожидания

            # Попробуем закрыть всплывающее окно, если оно есть
            try:
                # Ожидаем появления кнопки "Закрыть"
                wait = WebDriverWait(driver, 10)
                close_button = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="ns-hmw0n-e-15"]//span[text()="Закрыть"]')))

                # Кликаем по кнопке "Закрыть"
                close_button.click()

                # Проверим, что кнопка "Закрыть" действительно исчезла
                wait.until(EC.staleness_of(close_button))

            except:
                pass  # Если всплывающего окна нет или не удается его закрыть, продолжаем выполнение


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
    print(f"Данные успешно записаны в файл: {file_path}")


if __name__ == "__main__":
        # Зададим диапозон обрабатываемых элементов списка
        # от 'start_index' до 'end_index' включая границы
        start_index = int(input("Первый индекс при старте: "))
        end_index = int(input("Индекс на финише: "))
        if end_index < start_index:
            end_index = start_index
        main(start_index, end_index)