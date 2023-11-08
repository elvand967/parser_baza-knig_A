# D:\Python\myProject\parser_baza-knig_A\module2_A(torrent_Null).py

import sqlite3
from module import write_json_file


# Функция для выборки данных и создания JSON-файла
def create_json_with_no_torrent(start_id, end_id):
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect("book_database.db")
    cursor = conn.cursor()

    # Выполняем SQL-запрос для выборки данных
    cursor.execute(
        'SELECT id, title, link, torrent FROM books WHERE id >= ? AND id <= ? AND (torrent IS NULL OR torrent = "Null")',
        (start_id, end_id))

    # Извлекаем выбранные строки
    rows = cursor.fetchall()

    # Закрываем соединение
    conn.close()

    # Создаем список словарей на основе выбранных строк
    data = []
    for row in rows:
        id, title, link, torrent = row
        data.append({
            "id": id,
            "title": title,
            "link": link,
            "torrent": torrent
        })


    # Определим рабочую директорию для *.json файла
    dir_Get ="JSONfiles\Get"  # Get (получить) - для дальнейшей обработки по скачиванию торрентов

    # Генерируем имя JSON-файла
    file_name = f'book_torrent({start_id}-{end_id})_no.json'

    # запишем данные в  *.json файл
    write_json_file(dir_Get, file_name, data)
    print(f'Создан файл: {file_name}')


# Запросим аргументы n и x
n = int(input("№ id при старте: "))
m = int(input("№ id на финише: "))
if m < n:
    m = n

# Вызываем функцию с заданными значениями n и x
create_json_with_no_torrent(n, m)


