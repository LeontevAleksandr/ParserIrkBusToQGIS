import json
from datetime import datetime


def remove_duplicates_and_sort(input_file, output_file):
    unique_objects = {}

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                data = json.loads(line.strip())  # Читаем строку как JSON
                data_str = json.dumps(data, sort_keys=True)  # Приводим к строке для уникальности
                if data_str not in unique_objects:
                    unique_objects[data_str] = data
            except json.JSONDecodeError:
                print("Ошибка декодирования JSON в строке:", line)
                continue

    def get_lasttime(obj):
        if 'anims' in obj and obj['anims']:
            return datetime.strptime(obj['anims'][0]['lasttime'], "%d.%m.%Y %H:%M:%S")
        return datetime.min  # Минимальное значение для сортировки пустых списков

    sorted_data = sorted(unique_objects.values(), key=get_lasttime)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for obj in sorted_data:
            outfile.write(json.dumps(obj, ensure_ascii=False) + "\n")


# Использование:
input_filename = "full_data.json"
output_filename = "delete_duplicate(test).json"
remove_duplicates_and_sort(input_filename, output_filename)