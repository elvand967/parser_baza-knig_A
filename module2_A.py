# D:\Python\myProject\parser_baza-knig_A\module2_A.py

'''
В этом модуле загружаем торрент-файлы, имеющиеся на web-страницах
URL которых полученны из book_database.db books (link).
При это загружаем только те торрент-файлы о которых записи в book_database.db torrent (torrent) нет.
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



# Директория в которой размещен исполняемый скрипт 'module2_A.py '
path_current_directory = os.path.abspath(os.path.dirname(__file__))


'''
Функции которая будет возвращать путь к директории Downloads 
установленный системой виндовс для скачивания файлов из интернета 
по умолчанию для браузеров (D:\\User\\Downloads).
Код открывает соответствующий ключ в реестре и получает значение пути к директории Downloads. 
Затем он проверяет, существует ли указанная директория. 
'''
def get_default_download_directory():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{374DE290-123F-4565-9164-39C4925E467B}"

    try:
        # Открываем соответствующий ключ в реестре
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # Получаем значение пути к директории Downloads
            download_path, _ = winreg.QueryValueEx(key, value_name)

            # Преобразуем в абсолютный путь
            download_path = os.path.expanduser(download_path)

            # Экранируем символы обратного слеша
            download_path = download_path.replace("\\", "\\\\")

            # Проверяем, существует ли директория
            if os.path.exists(download_path):
                return download_path
            else:
                print(f"The directory '{download_path}' does not exist.")
                return None

    except Exception as e:
        print(f"Error accessing the registry: {e}")
        return None


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
            downloads_torrent(path_GetJson_download_package)

    elif menu_mode == 2:  # 'Режим: "Регистрация загруженных данных в БД"'
        # Вызовим меню выбора пакетов загрузки
        path_SetJson_download_package = menu_packages_downloads(path_dir_Set, menu_mode)

        # если функция нам вернула путь к *.json файлу начнем загрузку в базу данных
        if path_SetJson_download_package is not None:
            print( f'Команда обновлять БД из {path_SetJson_download_package}')







# Меню: режим работы скрипта
def menu_script_mode():
    print('Режимы работы скрипта:\n****************')
    print('  1: Пакеты загрузки (обработка JSON, загрузка торрент файлов)')
    print('  2: Регистрация загруженных данных в БД\n****************')
    recd = int(input("Введите индекс режима работы: "))
    if recd == 1:
        my_print(MY_LOG, 'Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"')
        return 1
    elif recd == 2:
        my_print(MY_LOG, 'Режим: "Регистрация загруженных данных в БД"')
        return 2


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




''' Функция загрузки торрент-файлов.
Принимает полный путь к исходному JSON-файлу'''
def downloads_torrent(path_GetJson_download_package):
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
        print(f'id_db: {item["id"]}, книга `{item["title"]}`.')

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

            # Подождем еще 2-3 секунды
            t2 = random.randint(2, 3)
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


''' Простая функция транслитерации кирилицы в латиницу'''
def transliterate(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    result = []
    for char in text:
        lower_char = char.lower()
        result.append(translit_dict.get(lower_char, char))

    return ''.join(result)


'''Функция для очистки имени файла от специальных символов 
и с помощью функции transliterate(text) обеспечивает транслитерации (ru-en).
Заменит недопустимые символы на дефисы.
Заменит точки на нижнее подчеркивание.
Удалит повторяющиеся дефисы.
Удалит повторяющиеся нижние подчеркивания в имени файла
'''
def clean_filename(filename):
    # Замена недопустимых символов на дефис
    invalid_chars = {'/', '\\', ':', '*', '?', '"', '<', '>', '|'}
    filename = ''.join('-' if c in invalid_chars else c for c in filename)

    # Замена точек на нижнее подчеркивание
    filename = filename.replace('.', '_')

    # Удаление повторяющихся дефисов
    filename = '-'.join(filter(None, filename.split('-')))

    # Удаление повторяющихся нижних подчеркиваний
    filename = '_'.join(filter(None, filename.split('_')))

    return transliterate(filename)


''' Функция read_json_file(path_json_download_package) попытается 
открыть и прочитать JSON файл по указанному пути
и вернуть его содержимое в виде списка словарей.
Если файла нет, создадим его с пустым списком'''
def read_json_file(path_json_download_package):
    try:
        with open(path_json_download_package, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # print(f"Файл {path_json_download_package} - не найден.\nСоздан новый файл {file_path}.")
        data = []
        with open(path_json_download_package, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return data
    except json.JSONDecodeError:
        print(f"Ошибка при декодировании JSON файла: {path_json_download_package}")
        return None


''' Функция работает в режиме вывода сообщенией в окне терминала
и вместе с тем регистрирует все сообщения в текстовом файле'''
def my_print(name_path, text):
    # Проверяем наличие файла по принятому пути
    if os.path.exists(name_path):
        # Открываем файл для добавления текста
        with open(name_path, "a", encoding="utf-8") as file:
            # Добавляем переданный текст с новой строки
            file.write("\n" + text)
    else:
        # Создаем новый файл и записываем текст
        with open(name_path, "w", encoding="utf-8") as file:
            file.write(text)
    # Выводим текст в терминал
    print(text)


''' Функция принимает путь к директории и расширение файла,
возвращает список имеющихся в ней файлов с требуемым расширением
В случае ошибки возращает пустой список и сообщение о ошибке '''
def get_files_in_directory(dir_path, file_extension='.json'):
    try:
        file_list = [file for file in os.listdir(dir_path) if file.endswith(file_extension) and os.path.isfile(os.path.join(dir_path, file))]
        return file_list
    except Exception as e:
        print(f"An error occurred/Произошла ошибка:\n{e}")
        return []


''' Функция удаления файла '''
def delete_file(file_path, file_name):
    # Формируем полный путь к файлу
    full_path = os.path.join(file_path, file_name)

    try:
        # Удаляем файл
        os.remove(full_path)
        # print(f'Файл `{file_name}` успешно удален.')
    except FileNotFoundError:
        print(f'Файл {full_path} не найден.')
    except PermissionError:
        print(f'Отсутствуют права на удаление файла {full_path}.')
    except Exception as e:
        print(f'Произошла ошибка при удалении файла {full_path}: {e}')


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
    cursor.execute(
        '''
        SELECT books.id, books.title, books.link
        FROM books
        LEFT JOIN torrent ON books.link = torrent.link
        WHERE books.id >= ? AND books.id <= ? AND (torrent.link IS NULL OR torrent.torrent IS NULL OR torrent.torrent = "Null")
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

    # Соберем путь и запишем данные в *.json файл
    file_path = os.path.join(path_dir_Get, file_json_name)
    write_json_file(file_path, data)
    my_print(MY_LOG, f'Создан `пакет загрузки`: {file_json_name}')


''' Функция 'write_json_file(file_path, data)' принимает директорию, путь к JSON файлу
и список словарей (или других объектов, которые могут быть сериализованы в JSON)
Записывает данные (data) в указанный файл.
Если файл существует, он будет перезаписан новыми данными.   '''
def write_json_file(path_file_name, data):
    with open(path_file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


''' Функция изменяет части имен/путей файлов или добовляет постфиксы в имена файлов  '''
def remove_replace_substring_postfix(path_file_name, substring, new_substring=''):
    if substring is not None:
        # Заменить или удалить совпадающую подстроку
        new_path_file_name = path_file_name.replace(substring, new_substring)
        # Вернуть имя/путь с обработанным подстрокой
        return new_path_file_name
    else:
        # Если `substring` равен None, добавить new_substring перед точкой (расширением файла)
        base_path, extension = os.path.splitext(path_file_name)
        return base_path + new_substring + extension


'''
Функции которая будет возвращать путь к директории Downloads 
установленный системой виндовс для скачивания файлов из интернета 
по умолчанию для браузеров (D:\\User\\Downloads).
Код открывает соответствующий ключ в реестре и получает значение пути к директории Downloads. 
Затем он проверяет, существует ли указанная директория. 
'''
def get_default_download_directory():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{374DE290-123F-4565-9164-39C4925E467B}"

    try:
        # Открываем соответствующий ключ в реестре
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # Получаем значение пути к директории Downloads
            download_path, _ = winreg.QueryValueEx(key, value_name)

            # Преобразуем в абсолютный путь
            download_path = os.path.expanduser(download_path)

            # Экранируем символы обратного слеша
            download_path = download_path.replace("\\", "\\\\")

            # Проверяем, существует ли директория
            if os.path.exists(download_path):
                return download_path
            else:
                print(f"The directory '{download_path}' does not exist.")
                return None

    except Exception as e:
        print(f"Error accessing the registry: {e}")
        return None


''' функция format_time(seconds) преобразует количество секунд в формат "hh ч. mm м. ss с." '''
def format_time(seconds):
    # hours, remainder = divmod(seconds, 3600)
    # minutes, seconds = divmod(remainder, 60)
    if seconds >= 60:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}."
    else:
        return f"{int(seconds):02d} сек."



if __name__ == "__main__":
    main()
