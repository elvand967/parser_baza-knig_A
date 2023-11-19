# D:\Python\myProject\parser_baza-knig_A\utils.py
import shutil
import sqlite3
import json
import os
import winreg  # для доступа к реестру Windows при необходимости получения пути к папке загрузки браузеров по умолчанию
from datetime import datetime

# from setuptools.msvc import winreg



''' Функция работает в режиме вывода сообщенией в окне терминала
и вместе с тем регистрирует все сообщения в текстовом файле'''
def my_print(name_path, text):
    # Проверяем наличие файла по принятому пути
    if os.path.exists(name_path):
        # Открываем файл для добавления текста
        with open(name_path, "a", encoding="utf-8") as file:
            # Добавляем переданный текст с новой строки
            file.write("\n" + text)
    else:
        # Создаем новый файл и записываем текст
        with open(name_path, "w", encoding="utf-8") as file:
            file.write(text)
    # Выводим текст в терминал
    print(text)


'''
Функции которая будет возвращать путь к директории Downloads 
установленный системой виндовс для скачивания файлов из интернета 
по умолчанию для браузеров (D:\\User\\Downloads).
Код открывает соответствующий ключ в реестре и получает значение пути к директории Downloads. 
Затем он проверяет, существует ли указанная директория. 
'''
def get_default_download_directory():
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"
    value_name = "{374DE290-123F-4565-9164-39C4925E467B}"

    try:
        # Открываем соответствующий ключ в реестре
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            # Получаем значение пути к директории Downloads
            download_path, _ = winreg.QueryValueEx(key, value_name)

            # Преобразуем в абсолютный путь
            download_path = os.path.expanduser(download_path)

            # Экранируем символы обратного слеша
            download_path = download_path.replace("\\", "\\\\")

            # Проверяем, существует ли директория
            if os.path.exists(download_path):
                return download_path
            else:
                print(f"The directory '{download_path}' does not exist.")
                return None

    except Exception as e:
        print(f"Error accessing the registry: {e}")
        return None


''' Простая функция транслитерации кирилицы в латиницу'''
def transliterate(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }

    result = []
    for char in text:
        lower_char = char.lower()
        result.append(translit_dict.get(lower_char, char))

    return ''.join(result)


'''Функция для очистки имени файла от специальных символов 
и с помощью функции transliterate(text) обеспечивает транслитерации (ru-en).
Заменит недопустимые символы на дефисы.
Заменит точки на нижнее подчеркивание.
Удалит повторяющиеся дефисы.
Удалит повторяющиеся нижние подчеркивания в имени файла
'''
def clean_filename(filename):
    # Замена недопустимых символов на дефис
    invalid_chars = {'/', '\\', ':', '*', '?', '"', '<', '>', '|'}
    filename = ''.join('-' if c in invalid_chars else c for c in filename)

    # Замена точек на нижнее подчеркивание
    filename = filename.replace('.', '_')

    # Удаление повторяющихся дефисов
    filename = '-'.join(filter(None, filename.split('-')))

    # Удаление повторяющихся нижних подчеркиваний
    filename = '_'.join(filter(None, filename.split('_')))

    return transliterate(filename)


''' Функция read_json_file(path_json_download_package) попытается 
открыть и прочитать JSON файл по указанному пути
и вернуть его содержимое в виде списка словарей.
Если файла нет, создадим его с пустым списком'''
def read_json_file(path_json_download_package):
    try:
        with open(path_json_download_package, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        # print(f"Файл {path_json_download_package} - не найден.\nСоздан новый файл {file_path}.")
        data = []
        with open(path_json_download_package, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return data
    except json.JSONDecodeError:
        print(f"Ошибка при декодировании JSON файла: {path_json_download_package}")
        return None


''' Функция принимает путь к директории и расширение файла,
возвращает список имеющихся в ней файлов с требуемым расширением
В случае ошибки возращает пустой список и сообщение о ошибке '''
def get_files_in_directory(dir_path, file_extension='.json'):
    try:
        file_list = [file for file in os.listdir(dir_path) if file.endswith(file_extension) and os.path.isfile(os.path.join(dir_path, file))]
        return file_list
    except Exception as e:
        print(f"An error occurred/Произошла ошибка:\n{e}")
        return []


''' Функция удаления файла '''
def delete_file(file_path, file_name):
    # Формируем полный путь к файлу
    full_path = os.path.join(file_path, file_name)

    try:
        # Удаляем файл
        os.remove(full_path)
        # print(f'Файл `{file_name}` успешно удален.')
    except FileNotFoundError:
        print(f'Файл {full_path} не найден.')
    except PermissionError:
        print(f'Отсутствуют права на удаление файла {full_path}.')
    except Exception as e:
        print(f'Произошла ошибка при удалении файла {full_path}: {e}')


''' Функция изменяет части имен/путей файлов или добовляет постфиксы в имена файлов  '''
def remove_replace_substring_postfix(path_file_name, substring, new_substring=''):
    if substring is not None:
        # Заменить или удалить совпадающую подстроку
        new_path_file_name = path_file_name.replace(substring, new_substring)
        # Вернуть имя/путь с обработанным подстрокой
        return new_path_file_name
    else:
        # Если `substring` равен None, добавить new_substring перед точкой (расширением файла)
        base_path, extension = os.path.splitext(path_file_name)
        return base_path + new_substring + extension


''' функция format_time(seconds) преобразует количество секунд в формат "hh ч. mm м. ss с." '''
def format_time(seconds):
    if seconds >= 60:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}."
    else:
        return f"{int(seconds):02d} сек."


''' Функция 'write_json_file(file_path, data)' принимает директорию, путь к JSON файлу
и список словарей (или других объектов, которые могут быть сериализованы в JSON)
Записывает данные (data) в указанный файл.
Если файл существует, он будет перезаписан новыми данными.   '''
def write_json_file(path_file_name, data):
    with open(path_file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


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

# Вызов функции для создания резервной копии БД
# create_backup("D:\\Python\\myProject\\parser_baza-knig_A\\book_database.db", 'backup')
#++++++++++++++++++++++++++++++++++++++++++++++++++


''' Функция `def compare_database_and_files(database_path, downloads_path)`
Задача: провести сверку соответствия данных зафиксированных в таблице "torrent" с фактически имеющимися файлами в соответствующих подпапках
Вывести отчет о записях в таблице "torrent" для которых фактически нет файлов в требуемом месте,
а так-же отчет о файлах которые не учтены в таблице "torrent".
Если какого-либо несоотетствия не будет выявлено, так-же информировать об этом.
'''
def compare_database_and_files(database_path, downloads_path):
    try:
        # Подключение к базе данных
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Получение списка записей из таблицы "torrent"
        cursor.execute('SELECT link, torrent, path_torrent FROM torrent')
        db_records = cursor.fetchall()

        # Получение списка файлов на диске
        file_records = []
        for path_torrent, _, filenames in os.walk(downloads_path):
            for filename in filenames:
                file_records.append((os.path.join(path_torrent, filename), filename, os.path.relpath(path_torrent, downloads_path)))

        # Сравнение записей в базе данных и файлах на диске
        missing_files_db = [record for record in db_records if record[2] not in [file_record[2] for file_record in file_records]]
        missing_files_disk = [file_record for file_record in file_records if (file_record[2], file_record[1]) not in [(record[2], record[1]) for record in db_records]]

        # Вывод отчета
        if missing_files_db:
            print("Записи в базе данных без файлов на диске:")
            for link, torrent, path_torrent in missing_files_db:
                print(f"Link: {link}, Torrent: {torrent}, Path_torrent: {path_torrent}")

        if missing_files_disk:
            print("Файлы на диске без записей в базе данных:")
            for file_path, filename, path_torrent in missing_files_disk:
                print(f"File path: {file_path}, Filename: {filename}, Path_torrent: {path_torrent}")

        if not missing_files_db and not missing_files_disk:
            print("Несоответствие между базой данных и файлами на диске не выявлено.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    finally:
        # Закрытие соединения
        if conn:
            conn.close()

# Вызов `def compare_database_and_files(database_path, downloads_path)`
# compare_database_and_files("book_database.db", "D:\\Python\\myProject\\parser_baza-knig_A\\Downloads_torrent")
#++++++++++++++++++++++++++++++++++++++++++++++++++




