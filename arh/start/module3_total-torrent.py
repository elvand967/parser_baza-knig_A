# D:\Python\myProject\parser_baza-knig\module3_total-torrent.py

'''
Готовим *.json к формированию БД.

Анализируем результаты работы module2.py и формируем 2 *.json файла:
1) book_database_total.json (полный комплект данных)
2) book_database3.json (словари требующие дозагрузки только торрентов)

Источник  *.json вводим в ручном режиме выбором из доступных файлов по индексу

Как выяснелось, кроме неполного скачивания торрент-файлов, наш модуль module2.py
так-же не мало накосячил и пропустил некоторые ссылки
Еще возникает вопрос о скаченных картинка? К нему вернемся позже!!!
'''

import os
import json

def main():
    # Путь к директории результатов анализа
    dirJSONtotal = "JSONtotal"

    # Проверяем, существует ли "JSONtotal" - директория, для сохранения результатов,
    # и создаем её, если она не существует
    if not os.path.exists(dirJSONtotal):
        os.makedirs(dirJSONtotal)

    # Путь к директории исходных файлов для анализа
    dirJSONfiles = "JSONfiles"

    # переменная для хранения списка *.json файлов
    file_list =[]

    # Проверяем, существует ли "JSONfiles" - директория с исходными *.json файлами,
    # и создаем её, если она не существует
    if not os.path.exists(dirJSONfiles):
        os.makedirs(dirJSONfiles)
        print(f'Создана директория {dirJSONfiles},\nРазместите в ней *.json файлы, требующие обработки\nи повторите попытку!')
        # останавливаем работу функции
        return

    else:
        # Получаем список *.json файлов в директории 'dirJSONfiles', требующих обработки
        file_list = os.listdir(dirJSONfiles)

    # Отфильтруйте только файлы с расширением .json
    json_files = [file for file in file_list if file.endswith('.json')]

    print('Доступны:')
    # Формируем список для выбора файлов
    for i, choice in enumerate(json_files):
        print(f'{i}  {choice}')

    n = int(input("Выберите файл для анализа: "))
    # print(f'Будем обрабатывать {json_files[n]}')

    # Собираем полный путь к иследуемому JSON-файлу
    file_path = os.path.join(dirJSONfiles, json_files[n])
    # Получим содержимое иследуемого JSON-файла в виде списка словарей
    json_files_study = read_json_file(file_path)
    # print(f'Количество элементов в {file_path} равно {len(json_files_study)}')

    # Собираем полный путь к итоговому JSON-файлу "book_database_total.json"
    file_path = os.path.join(dirJSONtotal, 'book_database_total.json')
    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_total = read_json_file(file_path)
    print(f'Количество элементов в {file_path} равно: {len(json_files_total)}')


    # Собираем полный путь к итоговому JSON-файлу "book_database3.json"
    file_path = os.path.join(dirJSONtotal, 'book_database3.json')
    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_notTorrent = read_json_file(file_path)
    print(f'Количество элементов в {file_path} равно: {len(json_files_notTorrent)}')

    # total_link = read_json_file('book_database.json')
    # print(f'\nОбщее количество ссылок в "book_database.json" равно: {len(total_link)}')

    # Цикл для обработки каждого элемента из json_files_study
    for item in json_files_study:
        torrent_value = item.get("torrent")
        link_value = item.get("link")

        if torrent_value == "Ошибка":
            # Проверяем отсутствие такого-же словаря в json_files_notTorrent
            if not any(d.get("link") == link_value for d in json_files_notTorrent):
                json_files_notTorrent.append(item)
        else:
            # Проверяем отсутствие такого-же словаря в json_files_total
            if not any(d.get("link") == link_value for d in json_files_total):
                json_files_total.append(item)

    print('---------------------')


    # Собираем полный путь к итоговому JSON-файлу "book_database_total.json"
    file_path = os.path.join(dirJSONtotal, 'book_database_total.json')
    write_json_file(file_path, json_files_total)

    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_total = read_json_file(file_path)
    print(f'Количество элементов в {file_path} равно: {len(json_files_total)}')

    # Собираем полный путь к итоговому JSON-файлу "book_database3.json"
    file_path = os.path.join(dirJSONtotal, 'book_database3.json')
    write_json_file(file_path, json_files_notTorrent)

    # Получим содержимое итогового JSON-файла в виде списка словарей
    json_files_notTorrent = read_json_file(file_path)
    print(f'Количество элементов в {file_path} равно: {len(json_files_notTorrent)}')


'''
Функция read_json_file(file_path) попытается открыть и прочитать JSON файл по указанному пути 
и вернет его содержимое в виде словаря. 
Если файл не будет найден Функция создаст его,
Если произойдет ошибка при декодировании JSON - функция вернет None.
'''
def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Файл {file_path} - не найден.\nСоздан новый файл {file_path}.")
        data = []
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return data
    except json.JSONDecodeError:
        print(f"Ошибка при декодировании JSON файла: {file_path}")
        return None


'''
Функция 'write_json_file(file_path, data)' принимает путь к JSON файлу 
и список словарей (или других объектов, которые могут быть сериализованы в JSON) 
и записывает их в указанный файл. 
Если файл существует, он будет перезаписан новыми данными.
'''
def write_json_file(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Данные успешно записаны в файл: {file_path}")


if __name__ == "__main__":
        main()