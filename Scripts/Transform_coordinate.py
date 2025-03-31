import json


def convert_coordinates(obj):
    """Рекурсивно преобразует координаты lat и lon в объекте"""
    if isinstance(obj, dict):
        if 'lat' in obj and 'lon' in obj:
            obj['lat'] = (float(obj['lat']) / 1571673) - 0.002005
            obj['lon'] = (float(obj['lon']) / 1467000) - 0.002415
        for key, value in obj.items():
            convert_coordinates(value)
    elif isinstance(obj, list):
        for item in obj:
            convert_coordinates(item)


def process_file(input_file, output_file):
    """Обрабатывает файл с JSON (как строковый, так и отформатированный) и сохраняет результат"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Загружаем JSON как единую структуру

        convert_coordinates(data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except json.JSONDecodeError:
        print("Ошибка: Некорректный JSON в файле.")
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    process_file('filtered_data.json', 'refactor_json.json')
