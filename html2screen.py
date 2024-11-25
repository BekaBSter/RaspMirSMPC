import os
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor


def sync_html_to_screenshot(html_file, output_file, driver_path, browser_path):
    # Настройка параметров браузера
    options = Options()
    options.add_argument('--headless')  # Режим без графического интерфейса
    options.add_argument('--disable-gpu')  # Отключить GPU для стабильности
    options.add_argument('--window-size=1920,1080')  # Размер окна браузера
    options.binary_location = browser_path  # Указываем путь к Chrome/Chromium

    # Укажите путь к ChromeDriver
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Преобразуем путь к HTML-файлу в формат file:///
        absolute_html_path = os.path.abspath(html_file)
        html_url = f"file:///{absolute_html_path.replace(os.sep, '/')}"

        # Открываем HTML-файл
        driver.get(html_url)

        # Делаем скриншот
        driver.save_screenshot(output_file)
        print(f"Скриншот сохранен: {output_file}")
    finally:
        # Закрываем браузер
        driver.quit()


async def html_to_screenshot(html_file, output_file, driver_path, browser_path):
    loop = asyncio.get_event_loop()
    # Запуск синхронной функции в отдельном потоке
    await loop.run_in_executor(
        None,
        sync_html_to_screenshot,
        html_file, output_file, driver_path, browser_path
    )
