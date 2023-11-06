# D:\Python\myProject\parser_baza-knig_A\modul0db_A.py

import sqlite3
import json

# Открываем JSON-файл и загружаем данные
with open("arh/book_database.json", "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Устанавливаем соединение с базой данных
conn = sqlite3.connect("book_database.db")
cursor = conn.cursor()


# Создаем динамический SQL-запрос
for book in data:
    columns = ', '.join(book.keys())
    placeholders = ', '.join(['?'] * len(book))
    values = list(book.values())
    query = f'INSERT OR IGNORE INTO books ({columns}) VALUES ({placeholders})'

    try:
        # Выполняем SQL-запрос
        cursor.execute(query, values)
    except sqlite3.IntegrityError as e:
        print(f"Пропущена запись из-за ошибки целостности: {e}")
        continue

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()
