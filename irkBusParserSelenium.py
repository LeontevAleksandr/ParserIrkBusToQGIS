from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
import time
import logging
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser_selenium.log'),
        logging.StreamHandler()
    ]
)

# Конфигурация Chrome
CHROME_DRIVER_PATH = 'chromedriver.exe'  # Укажите правильный путь
CHROME_OPTIONS = Options()
#CHROME_OPTIONS.add_argument("--headless")  # Режим без GUI
CHROME_OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
CHROME_OPTIONS.add_experimental_option("excludeSwitches", ["enable-automation"])

# Параметры запроса
BASE_URL = "http://irkbus.ru/php/getVehiclesMarkers.php"
PARAMS = {
    "rids": "2-1",
    "lat0": 0,
    "lng0": 0,
    "lat1": 90,
    "lng1": 180,
    "curk": 0,
    "city": "irkutsk",
    "info": 12345,
    "_": None
}

CSV_HEADERS = [
    "id", "lon", "lat", "dir", "speed", "lasttime",
    "rid", "rnum", "rtype", "low_floor", "wifi"
]

def setup_driver():
    """Инициализация веб-драйвера"""
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=CHROME_OPTIONS)
    driver.execute_cdp_cmd(
        'Network.setUserAgentOverride',
        {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    )
    return driver

def capture_api_requests(driver, url_pattern):
    """Перехват сетевых запросов"""
    driver.execute_cdp_cmd('Network.enable', {})
    requests = []

    def listener(event):
        if url_pattern in event['params']['request']['url']:
            requests.append(event)

    driver.add_cdp_listener('Network.requestWillBeSent', listener)
    return requests

def parse_vehicle(vehicle):
    """Парсинг данных транспортного средства"""
    return {key: vehicle.get(key, '') for key in CSV_HEADERS}

def main():
    logging.info("Запуск Selenium парсера")

    driver = setup_driver()
    try:
        # Инициализация сессии
        driver.get("http://irkbus.ru/irkutsk")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Настройка перехвата запросов
        api_requests = capture_api_requests(driver, 'getVehiclesMarkers.php')

        with open('vehicles_data.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            if csvfile.tell() == 0:
                writer.writeheader()

            for _ in range(10):
                try:
                    # Генерация URL с актуальной временной меткой
                    PARAMS['_'] = int(datetime.now().timestamp() * 1000)
                    url = f"{BASE_URL}?{'&'.join([f'{k}={v}' for k, v in PARAMS.items()])}"

                    # Выполнение запроса через JavaScript
                    driver.execute_script(f"""
                        fetch('{url}')
                            .then(response => response.json())
                            .then(data => window.apiResponse = data)
                    """)

                    # Ожидание ответа
                    WebDriverWait(driver, 15).until(
                        lambda d: d.execute_script('return !!window.apiResponse'))

                    # Извлечение данных
                    result = driver.execute_script('return window.apiResponse')

                    if result.get('anims'):
                        for vehicle in result['anims']:
                            writer.writerow(parse_vehicle(vehicle))
                        logging.info(f"Записано {len(result['anims'])} записей")
                    else:
                        logging.warning("Нет данных в ответе")

                    # Случайная задержка
                    time.sleep(30 + abs(int.from_bytes(os.urandom(4), 'big') % 15))

                except Exception as e:
                    logging.error(f"Ошибка итерации: {str(e)}")
                    time.sleep(60)

    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}")
    finally:
        driver.quit()
        logging.info("Работа парсера завершена")

if __name__ == "__main__":
    main()