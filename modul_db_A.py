# D:\Python\myProject\parser_baza-knig_A\modul_db_A.py
import os
import sqlite3

def main():
    # add_new_column()
    # new_tabl()
    # print_name_columns("torrent")
    # drop_tabl()  # Удаление таблицы
    # new_tabl()



    #     directory = "D:\\Python\\myProject\\parser_baza-knig_A"
    #     database_files = find_all_databases(directory)
    #     if len(database_files) == 0:
    #         print(f'Нет доступных баз данных в директории {directory}')
    #     elif len(database_files) == 1:
    #         database = database_files[0]
    #         print(f'modul_db_A.py работает с  {database}')

    pass


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

    # Создаем таблицу для хранения данных
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            publication_date TEXT,
            title TEXT(250),
            link TEXT UNIQUE,
            author TEXT,
            reader TEXT,
            year TEXT,
            duration TEXT,
            quality TEXT,
            series TEXT,
            size TEXT,
            genre TEXT,
            description TEXT(5000),
            image_file TEXT UNIQUE,
            plot REAL,
            writing_talent REAL,
            characters REAL,
            voice_quality REAL,
            like INTEGER,
            dislike INTEGER,
            comments INTEGER,
            rating REAL
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


''' Создаем новую связанную таблицу'''
def new_tabl():
    # Подключение к базе данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # 1. Создаем таблицу "torrent"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS torrent (
            id INTEGER PRIMARY KEY,
            link TEXT UNIQUE,
            path_torrent_old TEXT,
            torrent_old TEXT,
            torrent TEXT UNIQUE,
            path_torrent TEXT,
            FOREIGN KEY (link) REFERENCES books (link)
        )
    ''')

    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()


''' Функция удаляет таблицу'''
def drop_tabl():
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Удаляем текущую таблицу
    cursor.execute("DROP TABLE books_temp")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()













if __name__ == "__main__":
    main()