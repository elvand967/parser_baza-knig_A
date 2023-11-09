# D:\Python\myProject\parser_baza-knig_A\module2_A(json_download-torrent).py

'''
В этом модуле загруаем торрент-файлы, имеющиеся на страницах
URL которых полученны по ключу "link" из принятых словарей *.json файла

Так-как данный парсер разробатывается под конкретный сайт,
не будем излишне заморачиваться с директориями и именами файлов.

В проекте создадим директории:
 - "JSONfiles/Get" - размещены *.json файлы источники URL
    - *.json файлы будем называть по шаблону "%Y-%m-%d_%H-%M_" + "book(1-2300)_torrent_no.json"

 - "JSONfiles/Set" - размещены *.json обновленные файлы с информацией о именах загруженных торрентов
    - *.json файлы будем называть по шаблону "%Y-%m-%d_%H-%M_" + "book(1-2300)_torrent_ThereIs.json"

Далее при запуске модуля будет формироваться список с именами файлов из директории "JSONfiles/Get"
Нужно выбрать индекс файла источника ввести его для дальнейшей работы модуля

В среднем планируется формировать *.json файлы источники объемом 1000-1300 словарей
При удачной загрузке торрент-файла на один словарь требуется 3-5 сек., что при удачном стечении может потребовать до 2-х часов
скачивания.

Далее будет выводиться информация о количестве зафиксированных словарей подлежащих проработке (*.json файлы - источники URL)
и количестве уже обработанных словарей
Следующим шагом будет определение диапозона индексов словарей источника подлежащих.

модуль начинает работу по скачиванию

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

from module import my_print, select_file, remove_replace_postfix, read_json_file, format_time, write_json_file
from datetime import datetime

# Формируем начальное значение MY_LOG с текущей датой и временем
now = datetime.now()
MY_LOG = now.strftime("%Y-%m-%d_%H-%M_")

def main():
    global MY_LOG
    MY_LOG += "json_download-torrent"

    # Определим рабочие директории
    dir_Get ="JSONfiles\Get"  # Get (получить) - для нашего модуля "JSONfiles\import"
    dir_Set = "JSONfiles\Set"  # Set (установить) - для нашего модуля "JSONfiles\export"

    my_print(MY_LOG, 'Для работы модуля: module2_A(json_download-torrent).py')

    # Выберем файл для обработки при помощи функции 'select_file(dir_import, MY_LOG)'
    file_json_Get = select_file(dir_Get, MY_LOG)

    # Если нажата клавиша "Esc" выходим из функции
    if file_json_Get is None:
        return  # Выход из функции


    # Получим содержимое исходного JSON-файла в виде списка словарей
    list_dict_json_Get = read_json_file(dir_Get, file_json_Get)

    # Генерируем имя JSON-файл "file_json_Set" из имени "file_json_Get",
    # Заменив у него постфикс '_no' на '_There_Is'
    file_json_Set = remove_replace_postfix(file_json_Get, '_no', '_There_Is')

    # Получим содержимое итогового JSON-файла в виде списка словарей
    list_dict_json_Set = read_json_file(dir_Set, file_json_Set)
    my_print(MY_LOG, f'Количество элементов в исходном {file_json_Get}: {len(list_dict_json_Get)}\n')
    my_print(MY_LOG, f'\nКоличество элементов в итоговом {file_json_Set}: {len(list_dict_json_Set)}')

    # Зададим диапозон обрабатываемых элементов списка
    # от 'start_index' до 'end_index' включая границы
    flag = True
    max_index = len(list_dict_json_Get)-1
    while flag:
        start_index = int(input("Индекс при старте: "))
        end_index = int(input("Индекс на финише:  "))

        if end_index < start_index or end_index > max_index or start_index > max_index:
            my_print(MY_LOG, f'Установлено недопустимое соотношение индексов,\n'
                             f'или указан несуществыющий индекс из допустимых ([0]->[{max_index}]):\n'
                             f'start_index[{start_index}] -> end_index[{end_index}]')
            continuation = input("Введите 'S' для повторного ввода или любой другой символ для Выхода из программы: ")
            if continuation == 'S' or continuation == 's' or continuation == 'Ы' or continuation == 'ы':
                continue
            else:
                return
        flag = False

    my_print(MY_LOG, f'Установлен диапозон обработки словарей {file_json_Get} [{start_index}] -> [{end_index}]')

    # Выберем интересующий нас диапозон списка
    filtered_items = islice(list_dict_json_Get, start_index, end_index+1)
    count_filtered_items = len(filtered_items)  # количество словарей для обработки

    # Засекаем начало времени работы кода
    start_time_pars = time.time()
    formatted_start_time = datetime.fromtimestamp(start_time_pars).strftime("%Y.%m.%d %H:%M")
    my_print(MY_LOG, f'Время начала загрузки торрент-файлов: {formatted_start_time}')

    # счетчик загруженных торрент-файлов
    sum_torrent = 0

    # Начинаем грузить торрент-файла
    for i, item in enumerate(filtered_items):
        # засекаем время обработки URL - словаря страницы
        start_time_URL = time.time()

        page_url = item["link"]
        # Вызываем download_torrent_file для загрузки торрент-файла
        torrent_file = download_torrent_file(page_url)
        # my_print(MY_LOG,
        #          f'\nЗагрузка торрент-файла по индексу: [{i}] ({file_json_Get} id: {item["id"]})')
        print(f'\nЗагрузка торрент-файла №: [{i+1}] из {count_filtered_items}\n (id: {item["id"]}, {item["title"]})')

        # Фуксируем результат работы функции
        # (имя торрент-файла либо сообщение об ошибке)
        item["torrent"] = torrent_file

        if torrent_file == "Ошибка" or torrent_file == None or torrent_file == "Торрент не найден":
            end_time_URL = time.time()
            # Посчитаем количество секунд затраченное на обработку URL
            # и с помощью функции format_time(seconds) вернем в формате  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)

            my_print(MY_LOG, f'Неудачная попытка загрузки торрент-файла\n(id: {item["id"]}, {item["title"]}).\nВремя обработки URL: [{elapsed_time_URL}]')
            continue
        else:
            # При успешной загрузке торрент-файла внесем изменения в списки словарей
            list_dict_json_Set.append(item)  # Добавим новый словарь
            list_dict_json_Get.remove(item)  # Удолим старый словарь

            # Обновляем JSON-файл (export)
            write_json_file(dir_Set, file_json_Set, list_dict_json_Set)

            # Обновляем JSON-файл (import)
            write_json_file(dir_Get, file_json_Get, list_dict_json_Get)

            end_time_URL = time.time()
            # Посчитаем количество секунд затраченное на обработку URL
            # и с помощью функции format_time(seconds) вернем в формате  "hh:mm:ss"
            elapsed_time_URL = format_time(end_time_URL - start_time_URL)
            my_print(MY_LOG, f'Успешно загружен торрент-файл: {torrent_file}\n(id: {item["id"]}, {item["title"]}).\nВремя обработки URL: [{elapsed_time_URL}]')

            # Не забудим посчитать успешную загрузку
            sum_torrent += 1

    end_time_pars = time.time()
    elapsed_time_pars = end_time_pars - start_time_pars
    elapsed_time_formatted = format_time(elapsed_time_pars)

    my_print(MY_LOG, f"\n\nНа обработку {count_filtered_items} элементов, всего затрачено: {elapsed_time_formatted}")
    my_print(MY_LOG, f"Загружено: {sum_torrent} торрент-файлов\n")
    my_print(MY_LOG, f'Количество элементов в исходном {file_json_Get}: {len(list_dict_json_Get)}\n')
    my_print(MY_LOG, f'Количество элементов в итоговом {file_json_Set}: {len(list_dict_json_Set)}\n\n\n\n')

def download_torrent_file(url):
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
                # print("Торрент-файл не загружен.")
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
            # print(f"Торрент не найден на странице")
            driver.quit()
            return "Торрент не найден"

    except Exception as e:
        print(f"Ошибка при скачивании торрент-файла: {e}")
        driver.quit()
        return "Ошибка"


if __name__ == "__main__":
        main()