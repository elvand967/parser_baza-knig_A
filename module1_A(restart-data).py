# D:\Python\myProject\parser_baza-knig_A\modul_db_A.py

'''
Данный модуль разработан для загрузки из book_database.json в БД первичных данных
[
    {
        "id": 1,
        "title": "Не считая собаки",
        "link": "https://baza-knig.ink/popadancy/8-uillis-konni-ne-schitaya-sobaki.html"
    },
    ...
]
загруженных в начале раработки
'''


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
