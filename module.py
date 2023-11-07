# D:\Python\myProject\parser_baza-knig_A\module.py
import json
import os
import keyboard  # Импортируем модуль keyboard
import re


# Пример использования функции
# my_print("my_log", "Это текст для записи в лог-файл.")
def my_print(name, text):
    # Внешний каталог проекта
    project_dir = "D:\\Python\\myProject\\parser_baza-knig_arh"

    # Директория для хранения лог-файлов
    log_dir = os.path.join(project_dir, "log_files")

    # Создаем директорию, если она не существует
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Генерируем имя текстового файла
    filename = os.path.join(log_dir, f"{name}.txt")

    # Проверяем наличие файла
    if os.path.exists(filename):
        # Открываем файл для добавления текста
        with open(filename, "a", encoding="utf-8") as file:
            # Добавляем переданный текст с новой строки
            file.write("\n" + text)
    else:
        # Создаем новый файл и записываем текст
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)

    # Выводим текст в терминал
    print(text)


# Функция принимает путь к директории и возвращает список имеющихся в ней файлов
# В случае ошибки возращает пустой список и сообщение о ошибке
def get_files_in_directory(dir_import):
    try:
        file_list = os.listdir(dir_import)
        return file_list
    except Exception as e:
        my_print(f"An error occurred/Произошла ошибка:\n{e}")
        return []


# Функция выбора файла из директории
# def select_file(dir_import, MY_LOG):
#     files = get_files_in_directory(dir_import)
#
#     my_print(MY_LOG, "доступны файлы:")
#     for i, file in enumerate(files):
#         my_print(MY_LOG, f"{i}: {file}")
#
#     my_print(MY_LOG, "\nДля выбора введите индекс файла или нажмите 'Esc' для выхода:")
#
#     while True:
#         try:
#             key_event = keyboard.read_event()
#             if key_event.event_type == keyboard.KEY_DOWN:
#                 if key_event.name == 'esc':
#                     my_print(MY_LOG, "Нажата клавиша 'Esc', выходим из программы.")
#                     return None
#                 elif key_event.event_type == keyboard.KEY_DOWN and key_event.name.isnumeric():
#                     i = int(key_event.name)
#                     if 0 <= i < len(files):
#                         file_json_import = files[i]
#                         my_print(MY_LOG, f'Выбран: {file_json_import}')
#                         return file_json_import
#         except keyboard.read_event():
#             pass

def select_file(dir_import, MY_LOG):
    files = get_files_in_directory(dir_import)

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



# Функция изменяет или добовляет постфиксы в имена файлов
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


# Функция принимает путь директории, имя JSON-файла
# в возвращает его содержимое в виде списка элементов JSON-файла.
# Если принятой директории или файла нет, то создает их
# def read_json_file(dir_path, file_name):
#     # Проверяем, существует ли указанная директория
#     if not os.path.exists(dir_path):
#         os.makedirs(dir_path)  # Создаем директорию, если она не существует
#
#     file_path = os.path.join(dir_path, file_name)
#
#     # Проверяем, существует ли указанный файл
#     if not os.path.exists(file_path):
#         # Создаем пустой файл, если он не существует
#         with open(file_path, "w") as json_file:
#             json.dump([], json_file)
#
#     # Читаем содержимое JSON-файла
#     with open(file_path, "r") as json_file:
#         data = json.load(json_file)
#
#     return data

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