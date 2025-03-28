import random
import requests
import csv
import time
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,  # Измените на INFO после отладки
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)

BASE_URL = "http://irkbus.ru/php/getVehiclesMarkers.php"
PARAMS = {
    "rids": "214-0,215-0",
    "lat0": 0,
    "lng0": 0,
    "lat1": 90,
    "lng1": 180,
    "curk": 1157227,
    "city": "irkutsk",
    "info": 12345,
    "_": None
}

# Обновленные заголовки (добавлены недостающие из вашего браузера)
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
    "Cookie": "_ga=GA1.2.575277900.1739768378; PHPSESSID=35qqs8kf2de0h34fla6f645dh4; _gid=GA1.2.513095526.1742733787; _ga_1333VHZZJ1=GS1.2.1742789400.7.1.1742790542.0.0.0"
}

CSV_HEADERS = [
    "id", "lon", "lat", "dir", "speed", "lasttime",
    "rid", "rnum", "rtype", "low_floor", "wifi"
]


def get_timestamp():
    """Генерирует текущую временную метку в миллисекундах."""
    return int(datetime.now().timestamp() * 1000)


def parse_vehicle(vehicle):
    """Извлекает данные из объекта транспортного средства."""
    return {key: vehicle.get(key, "") for key in CSV_HEADERS}


def main():
    logging.info("Запуск парсера")
    session = requests.Session()

    # Установка куки из заголовков
    session.headers.update(headers)

    try:
        with open("vehicles_data.csv", "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            if csvfile.tell() == 0:
                writer.writeheader()

            for attempt in range(20):  # Увеличено количество попыток
                try:
                    PARAMS["_"] = "1742790251850"

                    response = session.get(
                        BASE_URL,
                        params=PARAMS,
                        timeout=15,
                        headers=headers
                    )

                    logging.debug(f"Response headers: {response.headers}")
                    logging.debug(f"Response content: {response.text}")  # Для отладки

                    data = response.json()
                    print(response.status_code)
                    print(response.headers)
                    print(response.text)
                    vehicles = data.get("anims", [])

                    if not vehicles:
                        logging.warning(f"Пустой ответ. Полный JSON: {data}")
                        continue

                    for vehicle in vehicles:
                        writer.writerow(parse_vehicle(vehicle))

                    logging.info(f"Записано: {len(vehicles)} записей")
                    time.sleep(5 + random.randint(0, 5))

                except requests.exceptions.JSONDecodeError as e:
                    logging.error(f"Ошибка декодирования JSON: {str(e)}")
                    time.sleep(5)
                except Exception as e:
                    logging.error(f"Ошибка: {str(e)}")
                    time.sleep(5)

    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}")
    finally:
        logging.info("Работа завершена")


if __name__ == "__main__":
    main()