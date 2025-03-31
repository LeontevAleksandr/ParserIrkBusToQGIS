import json

def filter_bus_data(input_file, output_file, gos_num):
    filtered_anims = []
    maxk_values = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())  # Загружаем каждую строку как отдельный JSON
                maxk_values.append(data.get("maxk", 0))
                filtered_anims.extend([bus for bus in data.get("anims", []) if bus.get("gos_num") == gos_num])
            except json.JSONDecodeError as e:
                print(f"Ошибка разбора JSON: {e}")

    # Создаем итоговый JSON-объект
    filtered_data = {"maxk": max(maxk_values, default=0), "anims": filtered_anims}

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)

# Использование
input_file = "delete_duplicate(test).json"
output_file = "filtered_data(test).json"
bus_gos_num = "У114ЕО"

filter_bus_data(input_file, output_file, bus_gos_num)
print(f"Фильтрованный JSON сохранен в {output_file}")