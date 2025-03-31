import random
import requests
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
    "rids": "343-0,344-0",
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
    "Cookie": "_ga=GA1.2.983502318.1742110273; _gid=GA1.2.1466981958.1743389741; PHPSESSID=ghhret9k1tj22rd8h7ib8aadm6; _gat=1; _ga_1333VHZZJ1=GS1.2.1743419789.13.0.1743419789.0.0.0"
}

def convert_coords(lat, lon):
    try:
        real_lat = (float(lat) / 1571673) - 0.002005 # на данный момент координаты не преобразуются!
        real_lon = (float(lon) / 1467000) - 0.002415 # использовать Transfrom_coordinate.py для получения реальных координат
        return round(real_lat, 6), round(real_lon, 6)
    except (TypeError, ValueError) as e:
        logging.error(f"Conversion error: {str(e)}")
        return None, None

def save_full_json(data, filename="full_data.json"):
    """Сохраняет данные в JSON Lines формате"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            json_record = json.dumps(data, ensure_ascii=False)
            f.write(json_record + '\n')
        logging.info(f"Данные сохранены в {filename}")
    except Exception as e:
        logging.error(f"Ошибка сохранения JSON: {str(e)}")

def get_timestamp():
    return int(datetime.now().timestamp() * 1000 - 166320)

def main():
    logging.info("Запуск парсера")
    session = requests.Session()
    session.headers.update(headers)

    try:
        while True:  # Бесконечный цикл
            try:
                PARAMS["_"] = get_timestamp()

                response = session.get(
                    BASE_URL,
                    params=PARAMS,
                    timeout=15,
                    headers=headers
                )

                data = response.json()
                save_full_json(data)
                time.sleep(5 + random.randint(0, 5))

            except requests.exceptions.JSONDecodeError as e:
                logging.error(f"JSON decode error: {str(e)}")
                time.sleep(5)
            except Exception as e:
                logging.error(f"General error: {str(e)}")
                time.sleep(5)

    except KeyboardInterrupt:
        logging.info("Получен сигнал прерывания. Завершение работы...")
    except Exception as e:
        logging.critical(f"Critical error: {str(e)}")
    finally:
        logging.info("Работа завершена")

if __name__ == "__main__":
    main()