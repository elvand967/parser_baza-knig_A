# D:\Python\myProject\parser_baza-knig_A\modul_db_A.py
import os
import sqlite3
import shutil
from datetime import datetime


def main():
    db_file = 'book_database.db'
    create_backup(db_file)  # Создаем резервную копию БД

    # add_new_column()
    # new_tabl()
    # print_name_columns("torrent")
    # drop_tabl()  # Удаление таблицы
    # new_tabl()

    # drop_tabl('details')
    # new_tabl_details()

    # update_path_torrent()  # Вызов функции для выполнения запроса обновление путей торрент-файлов path//1000
    # drop_column()    # Удалаляем колонку таблицы "torrent"
    # count_path_torrent_records()  # подсчет торрент-файлов в папках согласно записей в БД


#++++++++++++++++++++++++++++++++++++++++++++++++++
def create_backup(db_file, backup_folder='backup'):
    # Создать папку для хранения резервных копий, если её нет
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    # Генерировать имя резервной копии с использованием даты и времени
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'{backup_folder}/book_database_backup_{timestamp}.db'

    try:
        # Создать резервную копию
        shutil.copy(db_file, backup_file)
        print(f'Резервная копия создана: {backup_file}')
    except Exception as e:
        print(f'Ошибка при создании резервной копии: {e}')
#++++++++++++++++++++++++++++++++++++++++++++++++++


''' Поиск всех баз данных SQLite в проекте,
воспользуемся стандартной библиотекой os для поиска файлов.
Функция находит все файлы с расширением ".db" 
(предполагая, что базы данных SQLite имеют это расширение)
и возращает список найденых БД'''
def find_all_databases(directory):
    database_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".db"):
                database_files.append(os.path.join(root, file))

    return database_files



''' Функция открывает или создает базу данных "new_database.db"
cоздает "new_tab" таблицу для хранения данных'''
def new_bd_end_tab(database):
    # Открываем или создаем базу данных
    conn = sqlite3.connect(database)

    # Получаем курсор для выполнения SQL-запросов
    cursor = conn.cursor()

    # Создаем таблицу для хранения данных "books"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT(250),
            link TEXT UNIQUE,
            there_torrent INTEGER
        )
    ''')

    # Сохраняем изменения и закрываем базу данных
    conn.commit()
    conn.close()
    return
    

''' Функция добавляет новую колонку'''
def add_new_column():
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Добавляем новую колонку "torrent_new" типа TEXT и делаем её уникальной
    cursor.execute("ALTER TABLE books ADD COLUMN torrent_new TEXT")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()


''' Функция выведет имена всех колонок таблицы'''
def print_name_columns(tabl):
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")

    # Создание объекта cursor
    cursor = conn.cursor()

    # Формируем SQL-запрос вручную, вставляя имя таблицы
    sql = "PRAGMA table_info({})".format(tabl)

    # Выполнение SQL-запроса
    cursor.execute(sql)

    # Получение результатов запроса
    columns = cursor.fetchall()

    # Вывод списка колонок
    for column in columns:
        print(column[1])  # Имя колонки находится во втором элементе кортежа

    # Закрываем соединение
    conn.close()


''' Создаем новую связанную таблицу `torrent` '''
def new_tabl_torrent():
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # 1. Создаем таблицу "torrent"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS torrent (
            id INTEGER PRIMARY KEY,
            link TEXT UNIQUE,
            torrent_old TEXT,
            torrent TEXT UNIQUE,
            path_torrent TEXT,
            FOREIGN KEY (link) REFERENCES books (link)
        )
    ''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


''' Создаем новую связанную таблицу `details` '''
def new_tabl_details():
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # 1. Создаем таблицу "details"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS details (
            id INTEGER PRIMARY KEY,
            id_books INTEGER,
            link TEXT UNIQUE,
            author TEXT,
            reading TEXT,
            year TEXT,
            duration TEXT,
            quality TEXT,  -- качество
            cycle TEXT,  -- цикл
            number_cycle TEXT,  -- номер в цикле
            size TEXT,  -- Размер
            genre TEXT,  -- жанр 
            description TEXT,  -- описание  
            picture TEXT UNIQUE,
            path_picture TEXT,        
            plot REAL,  -- сюжет
            writing_talent REAL,  -- писательский талант
            characters REAL,  -- персонажи
            voice_quality REAL,  -- качество голоса
            final_grade REAL,  -- итоговая оценка
            like INTEGER,
            dislike INTEGER,
            comments INTEGER,
            rating REAL,
            FOREIGN KEY (id_books) REFERENCES books (id)  -- Добавлена запятая перед FOREIGN
        )
    ''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()



''' Функция удаляет таблицу'''
def drop_tabl(name_tabl):
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Удаляем текущую таблицу
    cursor.execute(f"DROP TABLE {name_tabl}")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()


''' Функция создаст резервную копию БД, Удалит колонку таблицы "torrent" '''
def drop_column():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect("book_database.db")
        cursor = conn.cursor()

        # Отключение внешних ключей
        cursor.execute('PRAGMA foreign_keys=off;')

        # Создание временной таблицы
        cursor.execute('CREATE TABLE IF NOT EXISTS temp_torrent AS SELECT id, link, torrent_old, torrent, path_torrent FROM torrent')

        # Удаление основной таблицы
        cursor.execute('DROP TABLE torrent')

        # Переименование временной таблицы в основную
        cursor.execute('ALTER TABLE temp_torrent RENAME TO torrent')

        # Включение внешних ключей и фиксация изменений
        cursor.execute('PRAGMA foreign_keys=on;')
        conn.commit()

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        if conn:
            conn.rollback()

    finally:
        # Закрытие соединения
        if conn:
            conn.close()






''' Функция (SQL-запрос) выполняет обновление столбца `path_torrent` в таблице `torrent` 
на основе значений столбца `id` из таблицы `books`. 
В результате выполнения этого запроса, значения столбца `path_torrent` в таблице `torrent` 
будут обновлены на целый остаток от деления на 1000 значений столбца `id` из таблицы `books`, 
соответствующих тем же самым значениям `link`.
'''
def update_path_torrent():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect("book_database.db")
        cursor = conn.cursor()

        # SQL-запрос для обновления path_torrent
        update_query = '''
            UPDATE torrent
            SET path_torrent = (
                SELECT CAST(books.id / 1000 AS TEXT)
                FROM books
                WHERE books.link = torrent.link
            )
            WHERE EXISTS (
                SELECT 1
                FROM books
                WHERE books.link = torrent.link
            )
        '''

        # Выполнение запроса
        cursor.execute(update_query)

        # Фиксация изменений
        conn.commit()
        print("Данные успешно обновлены.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        if conn:
            conn.rollback()

    finally:
        # Закрытие соединения
        if conn:
            conn.close()


def count_path_torrent_records():
    try:
        # Подключение к базе данных
        conn = sqlite3.connect("book_database.db")
        cursor = conn.cursor()

        # SQL-запрос для подсчета количества записей для каждого значения path_torrent
        count_query = '''
            SELECT path_torrent, COUNT(*) AS record_count
            FROM torrent
            GROUP BY path_torrent
        '''

        # Выполнение запроса
        cursor.execute(count_query)

        # Получение результатов запроса
        results = cursor.fetchall()

        # Вывод результатов
        for row in results:
            path_torrent, record_count = row
            print(f"Значение path_torrent: {path_torrent}, Количество записей: {record_count}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Закрытие соединения
        if conn:
            conn.close()













if __name__ == "__main__":
    main()