import datetime
import json
import logging
import copy
from typing import Optional

import h3
import yandex_geocoder

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import model
from external.pg.client import PgClient
from external.yandex.geocoder.client import GeocoderClient
from external.config.yandex_configs import read_geocoder_config
from model.geo import GeoPointEncoder, make_hex_id, AddressInfo, GeoEncoder, Point, GeoDecoder
from resources.utils import get_path_for_saving

def read_already_fetched_houses_from_resources_file() -> list[AddressInfo]:
    with open(f'{get_path_for_saving()}/houses_geo_info.json') as f:
        try:
            return json.load(f, object_hook=GeoDecoder.default)
        except json.decoder.JSONDecodeError as e:
            logging.error(f"Not valid json file, file not exists or empty file. Error: {e}")
            return []


def read_already_fetched_houses_from_pg_client(addresses: list[str]) -> list[AddressInfo]:
    pg_client = PgClient()
    already_fetched = []
    all_address_info = pg_client.get_all_address_info()
    map_from_address_info_to_idx = {address_info.address: idx for idx, address_info in enumerate(all_address_info)}
    with logging_redirect_tqdm():
        for address in addresses:
            if address in map_from_address_info_to_idx:
                address_idx = map_from_address_info_to_idx[address]
                already_fetched.append(all_address_info[address_idx])

    return already_fetched


def read_already_fetched_houses(addresses) -> list[AddressInfo]:
    logging.debug("Starting reading prefetch from file")
    from_file = read_already_fetched_houses_from_resources_file()
    logging.debug("Starting reading prefetch from pg")
    from_pg: list[AddressInfo] = read_already_fetched_houses_from_pg_client(addresses)
    logging.debug("Combine two data into one")

    uniq_address_from_pg = {address_info.address for address_info in from_pg}
    for address_info in from_file:
        if address_info.address not in uniq_address_from_pg:
            from_pg.append(address_info)

    return from_pg

def get_from_geocoder(address: str, geocoder: GeocoderClient) -> AddressInfo | None:
    try:
        coordinates: model.geo.Point = geocoder.coordinates(address)
        return AddressInfo(
            created_at=datetime.datetime.now(),
            address=address,
            coordinates=coordinates,
            water_parameters=None,
            is_fetched_from_pg=False
        )
    except yandex_geocoder.exceptions.NothingFound as e:
        logging.warning(f'Not found coordinates for address={address}. e={e}')
    except yandex_geocoder.exceptions.InvalidKey as e:
        logging.error(f"Limit of requests reached. Consider changing api-key = {read_geocoder_config().api_key} or increasing limits")
    return None

def retrieve_addresses_info(addresses: list[str], geocoder_requests_limit=None):
    geocoder = GeocoderClient()

    houses: list[AddressInfo] = read_already_fetched_houses(addresses)
    already_fetched_addresses = {obj.address for obj in houses}

    with logging_redirect_tqdm():
        need_to_process_address = list(filter(lambda x: x not in already_fetched_addresses, addresses))
        need_to_process_address = need_to_process_address[:geocoder_requests_limit or 10]
        for address in tqdm(need_to_process_address, desc="Fetch coordinates from geocoder"):
            address_info = get_from_geocoder(address, geocoder)
            if address_info:
                houses.append(address_info)

    # dump_addresses_to_file(houses)
    return houses

def retrieve_address_info(address: str) -> Optional[AddressInfo]:
    already_fetched_houses = read_already_fetched_houses([address])
    already_fetched_addresses = {obj.address: idx for idx, obj in enumerate(already_fetched_houses)}

    if address in already_fetched_addresses:
        return already_fetched_houses[already_fetched_addresses[address]]

    logging.info(f"Fetch address {address} from geocoder")
    geocoder = GeocoderClient()
    return get_from_geocoder(address, geocoder)


def dump_addresses_to_file(addresses_with_coordinates: list[AddressInfo]):
    with open(f'{get_path_for_saving()}/houses_geo_info.json', "w") as stream:
        json.dump(addresses_with_coordinates, stream, indent=4, ensure_ascii=False, cls=GeoEncoder)

def enrich_with_hexagons(addresses_with_coordinates, h3_resolution: int):
    enriched = copy.deepcopy(addresses_with_coordinates)
    for json_obj in enriched:
        lat = json_obj['coordinates']['latitude']
        lon = json_obj['coordinates']['longitude']
        json_obj[make_hex_id(h3_resolution)] = h3.latlng_to_cell(lat, lon, h3_resolution)
    return enriched