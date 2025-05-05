import json
import logging
import copy
import h3
import yandex_geocoder

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from external.web.ato.client import get_all_addresses
from external.yandex.geocoder.client import GeocoderClient
from model.geo import GeoPointEncoder
from resources.utils import get_path_for_saving

def read_already_fetched_houses():
    with open(f'{get_path_for_saving()}/houses_geo_info.json') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError as e:
            logging.error("Not valid json file, file not exists or empty file")
            return []

def retrieve_houses():
    addresses = get_all_addresses()
    logging.info(f"starting geocoding of addresses. Input count = {len(addresses)}")
    geocoder = GeocoderClient()

    houses = read_already_fetched_houses() or []
    already_fetched_addresses = {obj['address'] for obj in houses}

    with logging_redirect_tqdm():
        need_to_process_address = list(filter(lambda x: x not in already_fetched_addresses, addresses))
        for address in tqdm(need_to_process_address[:100]):
            try:
                coordinates = geocoder.coordinates(address)
                houses.append({
                    'address': address,
                    'coordinates': coordinates
                })
            except yandex_geocoder.exceptions.NothingFound as e:
                logging.warning(f'Not found coordinates for address={address}. e={e}')
            except yandex_geocoder.exceptions.InvalidKey as e:
                logging.error("Limit of requests reached. Consider changing api-key or increasing limits")
    return houses

def dump_addresses_to_file(addresses_with_coordinates):
    with open(f'{get_path_for_saving()}/houses_geo_info.json', "w") as stream:
        json.dump(addresses_with_coordinates, stream, indent=4, ensure_ascii=False, cls=GeoPointEncoder)

def enrich_with_hexagons(addresses_with_coordinates, h3_resolution: int):
    enriched = copy.deepcopy(addresses_with_coordinates)
    for json_obj in enriched:
        lat = json_obj['coordinates']['latitude']
        lon = json_obj['coordinates']['longitude']
        json_obj['hex_id'] = h3.latlng_to_cell(lat, lon, h3_resolution)
    return enriched