import json
import logging
import yandex_geocoder
import jsonpickle
from tqdm import tqdm

from external.web.ato.client import get_all_addresses
from external.yandex.geocoder.client import GeocoderClient
from model.geo import GeoPointEncoder
from resources.utils import get_path_for_saving

def retrieve_houses():
    addresses = get_all_addresses()
    logging.info(f"starting geocoding of addresses. Input count = {len(addresses)}")
    geocoder = GeocoderClient()
    houses = []
    for address in tqdm(addresses):
        try:
            coordinates = geocoder.coordinates(address)
            houses.append({
                'address': address,
                'coordinates': coordinates
            })
        except yandex_geocoder.exceptions.NothingFound as e:
            logging.warning(f'Not found coordinates for address={address}. e={e}')
        except Exception as e:
            logging.error(e)
    return houses

def dump_addresses_to_file(addresses_with_coordinates):
    with open(f'{get_path_for_saving()}/houses_geo_info.json', "w") as stream:
        json.dump(addresses_with_coordinates, stream, indent=4, ensure_ascii=False, cls=GeoPointEncoder)

def retrieve_and_dump_addresses_to_file():
    addresses_with_coordinates = retrieve_houses()
    with open(f'{get_path_for_saving()}/houses_geo_info.json', "w") as stream:
        json.dump(addresses_with_coordinates, stream, indent=4, ensure_ascii=False, cls=GeoPointEncoder)