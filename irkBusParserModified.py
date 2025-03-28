import random
import requests
import csv
import json
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)

BASE_URL = "http://irkbus.ru/php/getVehiclesMarkers.php"
PARAMS = {
    "rids": "220-0,221-0",
    "lat0": 0,
    "lng0": 0,
    "lat1": 90,
    "lng1": 180,
    "curk": 0,
    "city": "irkutsk",
    "info": 12345,
    "_": None
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "ru,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "irkbus.ru",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 YaBrowser/25.2.0.0 Safari/537.36",
    "Referer": "http://irkbus.ru/irkutsk",
    "Cookie": "_ga=GA1.2.575277900.1739768378; _gid=GA1.2.524279324.1743070307; PHPSESSID=ul09cq5geevhdqu8fpf7kl2jj1; _ga_1333VHZZJ1=GS1.2.1743154455.13.0.1743154455.0.0.0"
}

CSV_HEADERS = [
    "id", "lon", "lat", "dir", "speed", "lasttime",
    "rid", "rnum", "rtype", "low_floor", "wifi"
]


def convert_coords(lat, lon):
    try:
        real_lat = (float(lat) / 1571673) - 0.002005
        real_lon = (float(lon) / 1467000) - 0.002415
        return round(real_lat, 6), round(real_lon, 6)
    except (TypeError, ValueError) as e:
        logging.error(f"Conversion error: {str(e)}")
        return None, None

def transform_coordinates(data):
    """Рекурсивно преобразует координаты во всей структуре данных"""
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key in ['lat', 'lon']:
                # Преобразование координат
                converted = convert_coords(data[key], data[key] if key == 'lat' else data[key])
                if key == 'lat':
                    data[key] = converted[0]
                else:
                    data[key] = converted[1]
            else:
                data[key] = transform_coordinates(data[key])
        return data
    elif isinstance(data, list):
        return [transform_coordinates(item) for item in data]
    else:
        return data


def save_full_json(data, filename="full_data.json"):
    """Сохраняет полные данные в JSON-файл с преобразованными координатами"""
    try:
        # Преобразуем координаты во всей структуре
        transformed_data = transform_coordinates(data)

        # Загружаем существующие данные
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except FileNotFoundError:
            existing_data = []

        # Добавляем новые данные
        existing_data.append(transformed_data)

        # Сохраняем обновленные данные
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Данные сохранены в {filename}")
    except Exception as e:
        logging.error(f"Ошибка сохранения JSON: {str(e)}")


def parse_vehicle(vehicle):
    parsed = {key: vehicle.get(key, "") for key in CSV_HEADERS}

    # Преобразование координат
    lat = vehicle.get('lat')
    lon = vehicle.get('lon')
    real_lat, real_lon = convert_coords(lat, lon)
    if real_lat and real_lon:
        parsed['lat'] = real_lat
        parsed['lon'] = real_lon

    return parsed


def get_timestamp():
    return int(datetime.now().timestamp() * 1000 + 2880)


def main():
    logging.info("Запуск парсера")
    session = requests.Session()
    session.headers.update(headers)

    try:
        with open("vehicles_data.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            if csvfile.tell() == 0:
                writer.writeheader()

            for attempt in range(20):
                try:
                    PARAMS["_"] = get_timestamp()

                    response = session.get(
                        BASE_URL,
                        params=PARAMS,
                        timeout=15,
                        headers=headers
                    )

                    data = response.json()

                    # Сохраняем полные данные в JSON
                    save_full_json(data)

                    vehicles = data.get("anims", [])

                    for vehicle in vehicles:
                        parsed_vehicle = parse_vehicle(vehicle)
                        writer.writerow(parsed_vehicle)

                    logging.info(f"CSV: записано {len(vehicles)} записей")
                    time.sleep(5 + random.randint(0, 5))

                except requests.exceptions.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {str(e)}")
                    time.sleep(5)
                except Exception as e:
                    logging.error(f"General error: {str(e)}")
                    time.sleep(5)

    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
    finally:
        logging.info("Работа завершена")


if __name__ == "__main__":
    main()