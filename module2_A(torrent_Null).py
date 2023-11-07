import sqlite3
import json


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
    result_data = []
    for row in rows:
        id, title, link, torrent = row
        result_data.append({
            "id": id,
            "title": title,
            "link": link,
            "torrent": torrent
        })

    # Создаем JSON-файл
    filename = f'book_no_torrent({start_id}-{end_id}).json'
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(result_data, json_file, ensure_ascii=False, indent=4)


# Запросим аргументы n и x
n = int(input("№ id при старте: "))
m = int(input("№ id на финише: "))
if m < n:
    m = n

# Вызываем функцию с заданными значениями n и x
create_json_with_no_torrent(n, m)

print(f'Создан файл: book_no_torrent({n}-{m}).json')
