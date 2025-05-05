import logging

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

from resources.utils import get_path_for_saving

def get_streets_for_letter(letter_num, session):
    """Получаем список всех улиц для указанной буквы"""
    url = f"https://ato.by/streets/letter/{letter_num}"
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        street_links = soup.select('div.intro ul li a[href^="/street/"]')
        if not street_links:
            return []

        streets = []
        for link in street_links:
            street_name = link.get_text(strip=True)
            street_num = link['href'].split('/')[-1]  # Извлекаем номер улицы из URL
            streets.append({
                'name': street_name,
                'num': street_num
            })

        return streets

    except Exception as e:
        logging.error(f"Ошибка при получении улиц для буквы {letter_num}: {e}")
        return []

def get_houses_for_street(street_num, session):
    """Получаем все дома для указанной улицы"""
    url = f"https://ato.by/street/{street_num}"
    try:
        response = session.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        house_select = soup.find('select', {'id': 'hSHouseId'})
        if not house_select:
            return []

        houses = []
        for option in house_select.find_all('option'):
            if option['value'] != '0':  # Пропускаем первый option
                house_number = option.get_text(strip=True)
                houses.append(house_number)

        return houses

    except Exception as e:
        logging.error(f"Ошибка при получении домов для улицы {street_num}: {e}")
        return []

def get_all_addresses():
    """Получаем все адреса Минска"""
    addresses = []
    geo_prefix = 'Республика Беларусь, г. Минск'

    with open(f'{get_path_for_saving()}/minsk_addresses.txt') as f:
        lines = f.read().splitlines()
        return [f'{geo_prefix}, {address}' for address in lines]

    with requests.Session() as session:
        logging.info(f'ATO.BY client. Starting web-scraping.')
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        for letter_num in tqdm(range(1, 33)):
            # logging.info(f"Processing letter #{letter_num}")

            streets = get_streets_for_letter(letter_num, session)
            if not streets:
                continue

            for street in streets:
                houses = get_houses_for_street(street['num'], session)
                for house in houses:
                    full_address = f"{street['name']}, {house}"
                    addresses.append(f'{geo_prefix}, {full_address}')

    return addresses
