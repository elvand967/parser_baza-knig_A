import sqlite3
import json

json_file_imp = "JSONfiles/Get/book_database_total.json"
imp_path = "JSONfiles/Get/" + json_file_imp

# Открываем JSON-файл и загружаем данные
with open(imp_path, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)

# Создадим словарь сопоставления полей:
field_mapping = {
    "id": "id",
    "publication date": "publication_date",
    "title": "title",
    "link": "link",
    "avtor": "author",
    "chitaet": "reader",
    "god": "year",
    "dlitel'nost'": "duration",
    "kachestvo": "quality",
    "tsikl": "series",
    "razmer": "size",
    "zhanr": "genre",
    "description": "description",
    "image_file": "image_file",
    "torrent": "torrent",
    "plot": "plot",
    "writing_talent": "writing_talent",
    "characters": "characters",
    "voice_quality": "voice_quality",
    "like": "like",
    "dislike": "dislike",
    "comments": "comments",
    "rating": "rating"
}

# Создадим счетчики
n = 0  # количество обработанных словарей
p = 0  # количество обработанных картинок
m = 0  # количество обработанных торрент-файлов

# Устанавливаем соединение с базой данных
conn = sqlite3.connect("../../book_database.db")
cursor = conn.cursor()

# Создаем динамический SQL-запрос для обновления данных
for book in data:
    n = n + 1
    # if book["image_file"]:
    #     p = p + 1

    if book["torrent"] != "Ошибка" and book["torrent"] != "Нет" and book["torrent"] is not None:
        m = m + 1

    # Формируем SET часть SQL-запроса для обновления полей
    set_statements = ', '.join(f'{field_mapping[key]} = ?' for key in book.keys() if key != 'link')
    values = [book[key] for key in book.keys() if key != 'link']

    # Формируем SQL-запрос для обновления данных, используя поле "link" для связи
    query = f'UPDATE books SET {set_statements} WHERE link = ?'

    try:
        # Выполняем SQL-запрос, передав значения для обновления
        cursor.execute(query, values + [book["link"]])
    except sqlite3.IntegrityError as e:
        print(f"Пропущена запись из-за ошибки целостности: {e}")
        continue

# Сохраняем изменения
conn.commit()

# Закрываем соединение
conn.close()

print(f'Всего в {json_file_imp} словарей: {n}')
print(f'В них сведения о: {p} картинках')
print(f'В них сведения о: {m} торрент-файлах')
