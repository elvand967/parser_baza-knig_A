# D:\Python\myProject\parser_baza-knig_A\module2_A.py

'''
В этом модуле загружаем торрент-файлы, имеющиеся на web-страницах
URL которых полученны из book_database.db books (link).
При это загружаем только те торрент-файлы о которых записи в book_database.db torrent (torrent) нет
Жагружаем те торрент-файлы которые еще не зарегестрированны в БД
'''
import json
import os
import sys
from datetime import datetime
import time



# Формируем имя лог-файла MY_LOG
now = datetime.now()
script_path = os.path.basename(sys.argv[0])
script_name, _ = os.path.splitext(script_path)
MY_LOG = now.strftime("%Y-%m-%d_%H-%M_") + script_name + ".txt"

def main():
    # определим основные директории

    # Директория в которой размещен исполняемый скрипт 'module2_A.py '
    path_current_directory = os.path.abspath(os.path.dirname(__file__))

    path_dir_Get = os.path.join(path_current_directory, "JSONfiles\\Get")
    if not os.path.exists(path_dir_Get):
        os.makedirs(path_dir_Get)  # Создаем директорию, если она не существует
    path_dir_Set = os.path.join(path_current_directory, "JSONfiles\\Set")
    if not os.path.exists(path_dir_Set):
        os.makedirs(path_dir_Set)  # -//-
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
        menu_packages_downloads(path_dir_Get)
    elif menu_mode == 2:  # 'Режим: "Регистрация загруженных данных в БД"'
        my_print(MY_LOG, f'работа режима "Регистрация загруженных данных в БД"')









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


# Меню: режим работы скрипта
def menu_script_mode():
    print('Режимы работы скрипта:')
    print('1: Пакеты загрузки (обработка JSON, загрузка торрент файлов)')
    print('2: Регистрация загруженных данных в БД')
    recd = int(input("Введите индекс режима работы: "))
    if recd == 1:
        my_print(MY_LOG, 'Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"')
        return 1
    elif recd == 2:
        my_print(MY_LOG, 'Режим: "Регистрация загруженных данных в БД"')
        return 2


# Функция меню, Режим: "Пакеты загрузки (обработка JSON, загрузка торрент файлов)"
def menu_packages_downloads(path_dir_Get):
    while True:
        # Получим список *.json файлов находящихся в директории `path_dir_Get`
        # используя функцию `get_files_in_directory(dir_path)`
        list_Get_json = get_files_in_directory(path_dir_Get)
        if len(list_Get_json):
            print('\nДоступны JSON-файлы `пакетов загрузки`:')
            for i, file in enumerate(list_Get_json):
                # Получим содержимое исходного JSON-файла в виде списка словарей
                # с помощью функции read_json(dir_path, file_name)
                list_dict_json_Get = read_json(path_dir_Get, file)
                if len(list_dict_json_Get) == 0:
                    delete_file(path_dir_Get, file)
                    continue
                print(f'{i} : {file}\t [{len(list_dict_json_Get)}]')
        else:
            print('\nНет доступных JSON-файлов `пакетов загрузки`:')
        print('N : создать новый `пакет загрузки` (New)\n---------------------')

        recd = input("Введите индекс `пакета загрузки` или\n`N` (создать новый): ")

        if recd.isdigit():  # если строка состоит из цифр
            i = int(recd)  # приведем к соответсвующемку типу
            if 0 <= i < len(list_Get_json):  # и проверим введен ли корректный (допустимый) индекс
                my_print(MY_LOG, f'Пакет загрузки: {list_Get_json[i]}')
                # Собираем полный путь к файлу
                selected_path_file = os.path.join(path_dir_Get, list_Get_json[i])
                return selected_path_file

        elif recd.isalpha():  # если строка состоит из букв
            if len(recd) == 1 and (recd.upper() == 'N' or recd.upper() == 'Т'):
                # Запустим функцию создания нового пакета загрузки
                print('Запустим функцию создания нового пакета загрузки')
                return
        # если сюда дошли, повторим попытку
        print('Некорректный ввод! Повторите попытку.')


''' Функция принимает путь к директории и возвращает список имеющихся в ней файлов
В случае ошибки возращает пустой список и сообщение о ошибке '''
def get_files_in_directory(dir_path):
    try:
        file_list = os.listdir(dir_path)
        return file_list
    except Exception as e:
        print(f"An error occurred/Произошла ошибка:\n{e}")
        return []


''' Функция read_json(dir_path, file_name) попытается открыть 
и прочитать JSON файл по указанному пути, вернуть его содержимое в виде словаря.
Если произойдет ошибка при декодировании JSON - функция вернет None.    '''
def read_json(dir_path, file_name):
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


''' Функция удаления файла '''
def delete_file(file_path, file_name):
    # Формируем полный путь к файлу
    full_path = os.path.join(file_path, file_name)

    try:
        # Удаляем файл
        os.remove(full_path)
        print(f'Файл `{file_name}` успешно удален.')
    except FileNotFoundError:
        print(f'Файл {full_path} не найден.')
    except PermissionError:
        print(f'Отсутствуют права на удаление файла {full_path}.')
    except Exception as e:
        print(f'Произошла ошибка при удалении файла {full_path}: {e}')
















if __name__ == "__main__":
    main()
