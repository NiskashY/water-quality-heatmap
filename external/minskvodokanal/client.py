"""
Клиент для сайта минскоговодоканала.
Предоставляем возможность получить данные о качестве воды с их сайта.

Поле __headers - имитирует запрос из браузера

ВАЖНО! для того чтобы драйвер завелся успешно - необходимо, чтобы путь до него был в переменной $PATH
"""

from model.water_parameters import WaterParameters
from model.geo import Point
from bs4 import BeautifulSoup
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


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
        chrome_options.add_argument("--headless=new")
        chrome_options.headless = True
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get(self.__url)

            input_field = driver.find_element(By.ID, "address-selector")
            input_field.send_keys(address)
            input_field.send_keys(Keys.RETURN)  # RETURN == ENTER

            print("start to wait")
            wait = WebDriverWait(driver, 1)  # Wait up to 10 seconds
            wait.until(EC.presence_of_element_located((By.ID, "info-params-0")))

            print("Successfully retrieved info from site")
            results = driver.find_elements(By.ID, "info-params-0")[0]
            rows = results.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")  # For data cells

                # Combine headers and cells (if headers exist)
                row_data = [cell.text for cell in cells[1:]]

                # Print the row data as a tab-separated string
                print("\t".join(row_data))
            print(results)
        finally:
            # Close the browser
            driver.quit()

        # response = requests.get(self.__url, headers=self.__headers)
        # print(response.status_code)
        # if response.status_code == 200:
        #     soup = BeautifulSoup(response.text, "html.parser")
        #     headlines = soup.find(
        #         "input",
        #         {"id": "address-selector"},
        #     )
        #     print(headlines)
        return None
