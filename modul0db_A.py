# D:\Python\myProject\parser_baza-knig_A\modul0db_A.py

import sqlite3

# ''' 
# Функция открывает или создает базу данных "new_database.db"
# cоздает "new_tab" таблицу для хранения данных
# '''

# def new_bd_end_tab():
#     # Открываем или создаем базу данных
#     conn = sqlite3.connect("book_database2.db")

#     # Получаем курсор для выполнения SQL-запросов
#     cursor = conn.cursor()

#     # Создаем таблицу для хранения данных
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS books (
#             id INTEGER PRIMARY KEY,
#             publication_date TEXT,
#             title TEXT(250),
#             link TEXT UNIQUE,
#             author TEXT,
#             reader TEXT,
#             year TEXT,
#             duration TEXT,
#             quality TEXT,
#             series TEXT,
#             size TEXT,
#             genre TEXT,
#             description TEXT(5000),
#             image_file TEXT UNIQUE,
#             torrent TEXT UNIQUE,
#             plot REAL,
#             writing_talent REAL,
#             characters REAL,
#             voice_quality REAL,
#             like INTEGER,
#             dislike INTEGER,
#             comments INTEGER,
#             rating REAL
#         )
#     ''')

#     # Сохраняем изменения и закрываем базу данных
#     conn.commit()
#     conn.close()

#     return
    
# new_bd_end_tab()



def new_add_columns():
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Добавляем новую колонку "torrent_new" типа TEXT и делаем её уникальной
    cursor.execute("ALTER TABLE books ADD COLUMN torrent_new TEXT UNIQUE")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    conn.close()
