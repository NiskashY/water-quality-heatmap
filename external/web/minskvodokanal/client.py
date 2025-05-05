"""
Клиент для сайта минскоговодоканала.
Предоставляем возможность получить данные о качестве воды с их сайта.

Поле __headers - имитирует запрос из браузера

ВАЖНО! для того чтобы драйвер завелся успешно - необходимо, чтобы путь до него был в переменной $PATH
"""

import time

import selenium

from model.water_parameters import Parameter, WaterParameters
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import logging


def parse_float(text: str) -> float:
    if "/" in text:
        text = text.split("/")[0].strip()
    if "-" in text:
        text = text.split("-")[1].strip()  # берем максимум
    if "<" in text:
        text = text[1:]
    if text == '':
        text = '0.0'
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


class MinskVodokanalClient:
    __url: str = "https://minskvodokanal.by/water/home/"

    """
    Создаем веб-сессию через библиотеку selenium.
    Я использую Chrome, так как это самый популярный браузер 
    (соответственно для него веб-драйвер найти легче всего)
    """

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        logging.info("Starting webdriver for minskvodokanal")
        self.__driver = webdriver.Chrome(options=chrome_options)
        self.__retries_count = 2
        logging.info("Webdriver started")

    def __del__(self):
        self.__driver.quit()

    def v1_request(self, address: str) -> Optional[WaterParameters]:
        has_errors = False
        for i in range(self.__retries_count):
            try:
                logging.info(f"MinskVodokanal GET request for {address}")
                self.__driver.get(self.__url)

                logging.debug("Send address to site")
                input_field = self.__driver .find_element(By.ID, "address-selector")
                input_field.send_keys(address)
                input_field.send_keys(Keys.RETURN)  # RETURN == ENTER

                logging.debug("Searching for info-params-0")
                table_name = "info-params-0"
                wait = WebDriverWait(self.__driver , 10)  # Wait up to 10 seconds
                wait.until(EC.presence_of_element_located((By.ID, table_name)))
                time.sleep(0.5)

                info_params = self.__driver.find_elements(By.ID, table_name)[0]
                rows = info_params.find_elements(By.TAG_NAME, "tr")
                if len(rows) == 0:
                    continue

                logging.debug("Start parsing into WaterParameters")
                wp = WaterParameters(
                    smell=parse_smell(rows[0].find_elements(By.TAG_NAME, "td")),
                    taste=parse_taste(rows[1].find_elements(By.TAG_NAME, "td")),
                    color=parse_color(rows[2].find_elements(By.TAG_NAME, "td")),
                    muddiness=parse_muddiness(rows[3].find_elements(By.TAG_NAME, "td")),
                    general_mineralization=parse_general_mineralization(
                        rows[4].find_elements(By.TAG_NAME, "td")
                    ),
                )
                return wp
            except selenium.common.exceptions.StaleElementReferenceException as e:
                logging.error(e)
                error_flag = True

        assert has_errors == False, "check errors in logs. Selenium failed to retrieve water parameters info"
        return None