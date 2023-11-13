# D:\Python\myProject\parser_baza-knig_A\module2_A.py

'''
В этом модуле загружаем торрент-файлы, имеющиеся на web-страницах
URL которых полученны из book_database.db books (link).
При это загружаем только те торрент-файлы о которых записи в book_database.db torrent (torrent) нет
Жагружаем те торрент-файлы которые еще не зарегестрированны в БД
'''
import os
import sys
from datetime import datetime



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

    my_print(MY_LOG, 'Вызов из main')
    download_pack_menu()


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


def download_pack_menu():
    my_print(MY_LOG, 'Вызов из download_pack_menu()')
    pass


if __name__ == "__main__":
    main()
