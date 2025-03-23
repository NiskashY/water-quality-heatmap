"""
Клиент для сайта минскоговодоканала.
Предоставляем возможность получить данные о качестве воды с их сайта.

Поле __headers - имитирует запрос из браузера

ВАЖНО! для того чтобы драйвер завелся успешно - необходимо, чтобы путь до него был в переменной $PATH
"""

import time

from model.water_parameters import Parameter, WaterParameters
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def parse_float(text: str) -> float:
    if "/" in text:
        text = text.split("/")[0].strip()
    if "-" in text:
        text = text.split("-")[1].strip()  # берем максимум
    if "<" in text:
        text = text[1:]
    return float(text.replace(",", "."))


def parse_smell(td):
    return Parameter(
        name=td[0].find_elements(By.TAG_NAME, "span")[0].text,
        units=td[1].text,
        value=parse_float(td[2].text),  # has format 0/0
        max_allowed_concentration=parse_float(td[3].text),
    )


def parse_taste(td):
    return Parameter(
        name=td[0].find_elements(By.TAG_NAME, "span")[0].text,
        units=td[1].text,
        value=parse_float(td[2].text),
        max_allowed_concentration=parse_float(td[3].text),
    )


def parse_color(td):
    return Parameter(
        name=td[0].find_elements(By.TAG_NAME, "span")[0].text,
        units=td[1].text,
        value=parse_float(td[2].text),
        max_allowed_concentration=parse_float(td[3].text),
    )


def parse_muddiness(td):
    return Parameter(
        name=td[0].find_elements(By.TAG_NAME, "span")[0].text,
        units=td[1].text,
        value=parse_float(td[2].text),
        max_allowed_concentration=parse_float(td[3].text),
    )


def parse_general_mineralization(td):
    return Parameter(
        name=td[0].find_elements(By.TAG_NAME, "span")[0].text,
        units=td[1].text,
        value=parse_float(td[2].text),
        max_allowed_concentration=parse_float(td[3].text),
    )


class Client:
    __url: str = "https://minskvodokanal.by/water/home/"
    __headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    """
    Создаем веб-сессию через библиотеку selenium.
    Я использую Chrome, так как это самы популярный браузер (соответсвенно для него веб-драйвер найти легче всего)
    
    Set up the WebDriver (e.g., Chrome)
    Replace with the path to your WebDriver if not in PATH
    Open the target web page
    Replace with the URL of your target page
    
    Locate the input field and fill it
    Replace with the appropriate locator
    Replace with the text you want to input
    
    Submit the form (if applicable)
    Simulate pressing Enter
    
    Wait for the page to process the input and update
    Wait up to 10 seconds
    Replace with the appropriate locator
    Parse the updated page content
    Replace with the appropriate locator
    Print the text of each result
    """

    def v1_request(self, address: str) -> Optional[WaterParameters]:
        chrome_options = Options()
        # chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(self.__url)

            input_field = driver.find_element(By.ID, "address-selector")
            input_field.send_keys(address)
            input_field.send_keys(Keys.RETURN)  # RETURN == ENTER

            print("start to wait")
            table_name = "info-params-0"
            wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
            wait.until(EC.presence_of_element_located((By.ID, table_name)))
            time.sleep(0.5)
            print("Successfully retrieved info from site")
            results = driver.find_elements(By.ID, table_name)
            info_params = results[0]
            rows = info_params.find_elements(By.TAG_NAME, "tr")

            return WaterParameters(
                smell=parse_smell(rows[0].find_elements(By.TAG_NAME, "td")),
                taste=parse_taste(rows[1].find_elements(By.TAG_NAME, "td")),
                color=parse_color(rows[2].find_elements(By.TAG_NAME, "td")),
                muddiness=parse_muddiness(rows[3].find_elements(By.TAG_NAME, "td")),
                general_mineralization=parse_general_mineralization(
                    rows[4].find_elements(By.TAG_NAME, "td")
                ),
            )
        finally:
            # Close the browser
            driver.quit()
