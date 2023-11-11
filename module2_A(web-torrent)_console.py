# D:\Python\myProject\parser_baza-knig_A\module2_A(web-torrent)_console.py

'''
В этом модуле обрабатываем загруженные торрент файлы.
-Лог-файлы пишем аналогично "module2_A(json_download-torrent)_console.py" - ???

Так-как данный парсер разробатывается под конкретный сайт,
не будем излишне заморачиваться с директориями и именами файлов.

В проекте используем директорию:
 - "JSONfiles/Set" - размещены *.json файлы с информацией о именах загруженных торрентов
    (book_torrent(5901-7100)_There_Is.json)
В проекте создадим директорию:
 - "JSONfiles/Set_web" - где будут размещены *.json файлы с информацие об обновленном торренте
    (book_torrent(5901-7100)_web.json):
    [
        {
        "id_books": - id из таблицы "books"
        "link": - url к странице загрузки торрента от первоисточника
        "path_torrent_old": - путь к директории где хранился торрент-фай после скачивания торрент-файл
        "torrent_old": - старое имя торрент-файла
        "torrent": -     новое имя торрент-файла
        "path_torrent": -директория куда будет скопирован переименованный торрент-файл
        ...
        },
        ...
    ]

После полного формирования *.json файла, его данные будут записанны в таблицу "torrent"



Переименованные и подтвержденные торрент-файлы будут храниться в общей директории
"D:\\Python\\myProject\\parser_baza-knig_arh\\Total_Downloads\\Total_torrent_web" и далее
в поддиректории ("0": 1-999; "1": 1000-1999; "2": 2000-2999 и т.д.) подпапки с номерами тысяч "id" таблицы "books"
'''

import os
import json
import shutil
import sqlite3

from module import my_print, select_file, remove_replace_postfix, read_json_file, \
    select_dir, clean_filename, continue_work
from datetime import datetime

# Формируем начальное значение MY_LOG с текущей датой и временем
now = datetime.now()
MY_LOG = now.strftime("%Y-%m-%d_%H-%M_")


def main():
    global MY_LOG
    MY_LOG += "json_download-torrent"
    my_print(MY_LOG, 'Модуль: module2_A(web-torrent)_console.py')

    # Определим рабочие директории
    # Директория - первоисточник *.json файлов
    dir_Set = "D:\\Python\\myProject\\parser_baza-knig_A\\JSONfiles\\Set"

    # Директория - с новыми *.json файлами, после сортировки и переименования
    dir_Set_web = "D:\\Python\\myProject\\parser_baza-knig_A\\JSONfiles\\Set_web"

    # Общая директория - первоисточник торрент-файлов
    General_directory_torrentfiles_old ="D:\\Python\\myProject\\parser_baza-knig_arh\\Total_Downloads\\Total_Downloads_torrent\\"

    # Директория - первоисточник торрент-файлов
    print('Определите расположение исходных торрент-фаыйлов,')
    directory_torrentfiles_old = select_dir(General_directory_torrentfiles_old, MY_LOG)
    # print(f'Выбрана директория источнок торрент-файлов: {directory_torrentfiles_old}')

    # Общая директория - обработанных торрент-файлов.
    # В ней размещаются подпапки с номерами тысяч "id" таблицы "books"
    # ("0": 1-999; "1": 1000-1999; "2": 2000-2999 и т.д.)
    General_directory_torrentfiles_total ="D:\\Python\\myProject\\parser_baza-knig_arh\\Total_Downloads\\Total_torrent_web"

    # Выберем файл для обработки при помощи функции 'select_file(dir_Set, MY_LOG)'
    print('\nВыберите *.json, для совместного анализа.')
    file_json_Set = select_file(dir_Set, MY_LOG)

    if file_json_Set is None:
        return  # Выход из функции

    # Получим содержимое исходного JSON-файла в виде списка словарей
    list_dict_json_Set = read_json_file(dir_Set, file_json_Set)

    # Генерируем имя JSON-файл "file_json_Set_web" из имени "file_json_Set",
    # Заменив у него постфикс '_There_Is' на '_web'
    file_json_Set_web = remove_replace_postfix(file_json_Set, '_There_Is', '_web')

    # Получим содержимое итогового JSON-файла в виде списка словарей
    list_dict_json_Set_web = read_json_file(dir_Set_web, file_json_Set_web)

    my_print(MY_LOG, f'\nКоличество элементов в исходном {file_json_Set}: {len(list_dict_json_Set)}')
    my_print(MY_LOG, f'Количество элементов в итоговом {file_json_Set_web}: {len(list_dict_json_Set_web)}\n')

    # Сверим установочные данные
    continue_work()

    # Начинаем копировать торрент-файлы
    success_count = 0
    failure_count = 0

    for i, item in enumerate(list_dict_json_Set):
        if process_torrent_file(directory_torrentfiles_old, General_directory_torrentfiles_total, item, list_dict_json_Set_web):
            success_count += 1
        else:
            failure_count += 1

    # # Сохраняем список в файл JSON
    # with open(dir_Set_web+"\\"+file_json_Set_web, "w", encoding="utf-8") as json_file:
    #     json.dump(list_dict_json_Set_web, json_file, ensure_ascii=False)

    # Сохраняем список в файл JSON с отступами и без экранирования ASCII.
    # Для удобочитаемости добавлены параметры indent и ensure_ascii
    # Параметр indent=2 добавляет отступы в файле JSON, делая его более удобочитаемым.
    with open(dir_Set_web + "\\" + file_json_Set_web, "w", encoding="utf-8") as json_file:
        json.dump(list_dict_json_Set_web, json_file, ensure_ascii=False, indent=2)

    print(f'Успешные итерации: {success_count},\nНеудачные итерации: {failure_count}')

    add_records_to_torrent_table(list_dict_json_Set_web)


def process_torrent_file(directory_torrentfiles_old, General_directory_torrentfiles_total, item, list_dict_json_Set_web):
    # Получаем значение id из словаря
    '''В данной строке item.get("id", 0),
    метод get() используется для получения значения из словаря item по ключу "id".
    Если ключ "id" присутствует в словаре item, то метод вернет соответствующее ему значение.
    Если ключа "id" нет в словаре, то метод вернет значение по умолчанию, в данном случае 0.

    Форма метода get() выглядит так:
    get(key, default), где key - это ключ, значение которого мы пытаемся получить,
    а default - значение по умолчанию, которое будет возвращено, если ключ отсутствует.'''

    # Генерируем путь для новой директории
    item_id = item.get("id", 0)
    subdirectory = str(item_id // 1000)

    path_directory_torrentfiles_total = os.path.join(General_directory_torrentfiles_total, subdirectory)
    # print(f'Сгенерирован путь к директории: {path_directory_torrentfiles_total}')

    # Получаем имя торрент-файла из словаря
    torrent_file_name = item.get("torrent")

    # Полный путь к исходному торрент-файлу
    source_torrent_file_path = os.path.join(directory_torrentfiles_old, torrent_file_name)

    # Проверяем наличие исходного торрент-файла
    if not os.path.exists(source_torrent_file_path):
        print(f'Отсутствует требуемый торрент-файл: {torrent_file_name}')
        return

    # Проверяем расширение файла
    if not torrent_file_name.lower().endswith(".torrent"):
        print(f'Игнорируем файл: {torrent_file_name}, так как его расширение не *.torrent')
        return

    # Генерируем новое имя для торрент-файла
    new_torrent_file_name = f'{clean_filename(item["title"]).replace(" ", "_")}_{item_id}.{torrent_file_name.split(".")[-1]}'

    # Полный путь к новому торрент-файлу
    destination_torrent_file_path = os.path.join(path_directory_torrentfiles_total, new_torrent_file_name)

    # Создаем новую директорию, если она не существует
    if not os.path.exists(path_directory_torrentfiles_total):
        os.makedirs(path_directory_torrentfiles_total)

    # Формируем словарь
    entry = {
        "id_books": item.get("id", 0),
        "link": item.get("link"),
        "path_torrent_old": directory_torrentfiles_old,
        "torrent_old": torrent_file_name,
        "torrent": new_torrent_file_name,
        "path_torrent": path_directory_torrentfiles_total,
    }

    try:
        # Копируем торрент-файл и переименовываем его
        shutil.copy2(source_torrent_file_path, destination_torrent_file_path)
        print(f'Торрент-файл успешно скопирован и переименован: {new_torrent_file_name}')

        # Добавляем словарь в список
        list_dict_json_Set_web.append(entry)
        return True

    except Exception as e:
        print(f'Ошибка при копировании торрент-файла: {e}')
        return False


def add_records_to_torrent_table_old(data_list):
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Счетчики
    successful_attempts = 0
    failed_attempts = 0

    for record in data_list:
        link = record.get("link")
        torrent_old = record.get("torrent_old")
        torrent = record.get("torrent")

        # Проверяем наличие записи с таким ключом или торрентами
        cursor.execute('SELECT * FROM torrent WHERE link = ? OR torrent_old = ? OR torrent = ?', (link, torrent_old, torrent))
        existing_record = cursor.fetchone()

        if existing_record:
            # Определяем, какое поле вызвало дублирование
            duplicate_field = "link" if existing_record[1] == link else ("torrent_old" if existing_record[3] == torrent_old else "torrent")
            print(f'Запись с дублирующим значением поля {duplicate_field} ({existing_record[1]}) уже существует. Пропускаем добавление.')
            failed_attempts += 1
            continue
        else:
            # Вставляем новую запись, так как записи с таким ключом не существует
            cursor.execute('''
                INSERT INTO torrent (link, path_torrent_old, torrent_old, torrent, path_torrent)
                VALUES (?, ?, ?, ?, ?)
            ''', (link, record.get("path_torrent_old"), torrent_old, torrent, record.get("path_torrent")))
            successful_attempts += 1

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    # Выводим сообщения
    print(f'Успешно добавлено записей в db: {successful_attempts}')
    print(f'Неудачных попыток добавления в db: {failed_attempts}')
    print(f'Всего попыток добавления в db: {successful_attempts + failed_attempts}')

def add_records_to_torrent_table(data_list):
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Счетчики
    successful_attempts = 0
    failed_attempts = 0

    for record in data_list:
        link = record.get("link")
        torrent = record.get("torrent")

        # Проверяем наличие записи с таким ключом или торрентом
        cursor.execute('SELECT * FROM torrent WHERE link = ? OR torrent = ?', (link, torrent))
        existing_record = cursor.fetchone()

        if existing_record:
            # Определяем, какое поле вызвало дублирование
            duplicate_field = "link" if existing_record[1] == link else "torrent"
            print(f'Запись с дублирующим значением поля {duplicate_field} ({existing_record[1]}) уже существует. Пропускаем добавление.')
            failed_attempts += 1
            continue
        else:
            # Вставляем новую запись, так как записи с таким ключом не существует
            cursor.execute('''
                INSERT INTO torrent (link, path_torrent_old, torrent_old, torrent, path_torrent)
                VALUES (?, ?, ?, ?, ?)
            ''', (link, record.get("path_torrent_old"), record.get("torrent_old"), torrent, record.get("path_torrent")))
            successful_attempts += 1

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

    # Выводим сообщения
    print(f'Успешно добавлено записей в db: {successful_attempts}')
    print(f'Неудачных попыток добавления в db: {failed_attempts}')
    print(f'Всего попыток добавления в db: {successful_attempts + failed_attempts}')



if __name__ == "__main__":
    main()