# D:\Python\myProject\parser_baza-knig_A\module.py
import json
import os
import sys
import winreg  # для доступа к реестру Windows

# Импортируем модуль keyboard
import keyboard
import re
from transliterate import translit, detect_language
from unidecode import unidecode
import time

''' Функция работает в режиме вывода сообщенией в окне терминала
и вместе с тем регистрирует все сообщения в текстовом файле
Пример использования функции
my_print("my_log", "Это текст для записи в лог-файл.")'''
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


''' Функция принимает путь к директории и возвращает список имеющихся в ней файлов
В случае ошибки возращает пустой список и сообщение о ошибке '''
def get_files_in_directory(dir_path):
    try:
        file_list = os.listdir(dir_path)
        return file_list
    except Exception as e:
        my_print(f"An error occurred/Произошла ошибка:\n{e}")
        return []


''' Функция принимает абсолютный путь к директории и возвращает список вложенных в нее папок'''
def get_subdirectories(directory_path):
    try:
        # Получаем список файлов и папок в указанной директории
        contents = os.listdir(directory_path)

        # Фильтруем только папки
        subdirectories = [item for item in contents if os.path.isdir(os.path.join(directory_path, item))]

        return subdirectories

    except Exception as e:
        print(f"Error: {e}")
        return None


''' 
Функция "select_dir()", принимает путь к общей директории.
При помощи функции "get_subdirectories(dir_path)" 
формирует список доступных директорий в ней и
- предлагает выбрать из списка доступные 
- или ввести новую директорию, которую функция создаст
и вернет путь к требуемой директории
- или возращает None для выхода из программы 
'''
def select_dir(dir_path, MY_LOG):
    dirs = get_subdirectories(dir_path)  # Список вложенных дерикторий
    if dirs is None:
        recd = input("Нет вложенных директорий.\nВведите имя для создания новой\n"
                             "или нажмите 'Q' для выхода:_")
        if len(recd) == 1 and (recd.upper() == 'Q' or recd.upper() == 'Й'):
            return None  # вернем отсутствие значения выбора
        else:
            # Собираем полный путь к новой директории
            selected_dir = os.path.join(dir_path, recd)

            # Проверяем, существует ли указанная директория
            if not os.path.exists(selected_dir):
                os.makedirs(selected_dir)  # Создаем директорию, если она не существует
            my_print(MY_LOG, f'Создана новая директория: {selected_dir}')
            return selected_dir

    while True:
        print("Доступны директории:")
        for i, directory in enumerate(dirs):
            print(f"{i}: {directory}")
        recd = input("Введите индекс требуемой директории\n"
                                 "или имя, для создания новой.\n"
                     "Для выхода нажмите 'Q':_")

        if recd.isdigit():  # если строка состоит из цифр
            i = int(recd)   # приведем к соответсвующемку типу
            if 0 <= i < len(dirs):  # и введен корректный (допустимый) индекс
                # Собираем полный путь к директории
                selected_dir = os.path.join(dir_path, dirs[i])
                my_print(MY_LOG, f'Выбрана директория: {selected_dir}')
                return selected_dir
            else:
                return None  # вернем отсутствие значения

        elif recd.isalnum():  # если строка состоит из букв и цифр
            if len(recd) == 1 and (recd.upper() == 'Q' or recd.upper() == 'Й'):
                return None  # вернем отсутствие значения выбора
            else:
                # Собираем полный путь к новой директории
                selected_dir = os.path.join(dir_path, recd)

                # Проверяем, существует ли указанная директория
                if not os.path.exists(selected_dir):
                    os.makedirs(selected_dir)  # Создаем директорию, если она не существует
                my_print(MY_LOG, f'Создана новая директория: {selected_dir}')
                return selected_dir

        # другие символы и сочетания
        else:
            print('Некорректный ввод! Повторите попытку.')




''' Функция select_file() получив список файлов
находящихся в заданной директории при помощи функции get_files_in_directory()
предоставляет пользователю выбора требуемого файла путем ввода индекса
списока имеющихся в ней файлов
Возвращает имя выбранного файла
Предусмотрена обработка ошибок ввода несуществующего индекса
так-же остановка работы кода путем нажатия клавиши 'Esc'    '''
def select_file(dir_path, MY_LOG):
    files = get_files_in_directory(dir_path)

    my_print(MY_LOG, "доступны файлы:")
    for i, file in enumerate(files):
        my_print(MY_LOG, f"{i}: {file}")

    my_print(MY_LOG, "\nДля выбора введите индекс файла или нажмите 'Esc' для выхода:")

    while True:
        try:
            key_event = keyboard.read_event()
            if key_event.event_type == keyboard.KEY_DOWN:
                if key_event.name == 'esc':
                    my_print(MY_LOG, "Нажата клавиша 'Esc', выходим из программы.")
                    return None
                elif key_event.event_type == keyboard.KEY_DOWN and key_event.name.isnumeric():
                    i = int(key_event.name)
                    if 0 <= i < len(files):
                        file_json_import = files[i]
                        my_print(MY_LOG, f'Выбран: {file_json_import}')
                        return file_json_import
                    else:
                        my_print(MY_LOG, f'Ошибка: Введен недопустимый индекс. Попробуйте еще раз.')
        except ValueError:
            my_print(MY_LOG, f'Ошибка: Некорректный ввод. Введите индекс файла или нажмите "Esc" для выхода.')
        except keyboard.read_event():
            pass


''' Функция изменяет части имен файлов или добовляет постфиксы в имена файлов  '''
def remove_replace_postfix(file_name, text, new_text=''):
    if text is not None:
        # Заменить или удалить совпадающий текст
        new_name = file_name.replace(text, new_text)

        # Вернуть имя с обработанным текстом
        return new_name
    else:
        # Если text равен None, добавить new_text перед точкой
        base_name, extension = os.path.splitext(file_name)
        return base_name + new_text + extension


''' Функция read_json_file(dir_path, file_name) попытается открыть и прочитать JSON файл по указанному пути
и вернуть его содержимое в виде словаря.
Если директория или файл не будет найден Функция создаст их,
Если произойдет ошибка при декодировании JSON - функция вернет None.    '''
def read_json_file(dir_path, file_name):
    # Проверяем, существует ли указанная директория
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)  # Создаем директорию, если она не существует

    # Собираем полный путь к JSON-файлу
    file_path = os.path.join(dir_path, file_name)

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


''' Функция 'write_json_file(file_path, data)' принимает директорию, путь к JSON файлу
и список словарей (или других объектов, которые могут быть сериализованы в JSON)
Записывает данные (data) в указанный файл.
Если файл существует, он будет перезаписан новыми данными.   '''
def write_json_file(dir_path, file_name, data):
    # Собираем полный путь к JSON-файлу
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    # print(f"Данные успешно записаны в файл: {file_path}")


''' функция format_time(seconds) преобразует количество секунд в формат "hh ч. mm м. ss с." '''
def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d} ч. {int(minutes):02d} м. {int(seconds):02d} с."


'''Функция принимает путь к основной директории и диапозон чисел,
после чего в основной директории создает папки с именами этих чисел'''
def create_subdirectories(base_dir, start_range, end_range):
    # Создаем основную директорию, если она не существует
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Создаем поддиректории в указанном диапазоне
    for number in range(start_range, end_range + 1):
        subdirectory = os.path.join(base_dir, str(number))
        os.makedirs(subdirectory)
        print(f'Создана поддиректория: {subdirectory}')


'''функция clean_filename удалит все символы, кроме букв, цифр, пробелов, точек и подчеркиваний, 
что должно помочь избежать проблем с именами файлов.
Так-же будет использовать транслитерацию в латиницу для удаления специальных символов из имени файла.'''
def clean_filename(filename):
    return unidecode(''.join(c for c in filename if c.isalnum() or c in (' ', '.', '_')))


'''Функция приостанавливает работу скрипта и запрашивает подтверждение на продолжение работы
В случае отказа останавливает код'''
def continue_work():
    print("Подтвердите продолжение работы нажатием любой клавиши\nили нажмите 'Esc', для выхода из программы.")

    while True:
        if keyboard.is_pressed('esc'):
            print("Нажата клавиша 'Esc', выходим из программы.")
            sys.exit()
        else:
            return

        # Добавьте небольшую задержку, чтобы не загружать процессор
        time.sleep(0.1)




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










