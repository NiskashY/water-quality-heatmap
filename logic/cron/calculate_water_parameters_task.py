import logging
import random

from tqdm import tqdm
import more_itertools as mit

from external.config.water_config import read_water_config, WaterConfig
from external.pg.client import PgClient
from external.web.ato.client import get_all_addresses
from external.config.yandex_configs import GeocoderConfig, read_geocoder_config

from logic.geo.houses import retrieve_addresses_info
from logic.water_quality.color import determine_color
from logic.water_quality.water_parameters import retrieve_water_parameters, compute_avg_parameters_by_hexagons

from model.geo import AddressInfo
from model.water_parameters import WaterParameters

def count_consecutive_none(arr):
    max_count = current_count = 0
    for item in arr:
        if item is None:
            current_count += 1
            max_count = max(max_count, current_count)
        else:
            current_count = 0
    return max_count


def need_to_skip_saving(
        address_info: AddressInfo,
        fetched_water_parameters: WaterParameters,
        all_addresses_info_in_pg: dict[str, AddressInfo]
):
    if address_info.address in all_addresses_info_in_pg:
        already_saved_info = all_addresses_info_in_pg[address_info.address]
        if already_saved_info.water_parameters == fetched_water_parameters:
            return True
        if already_saved_info.water_parameters is not None:
            if fetched_water_parameters is None:
                # we fetched empty water params, but inside pg already stored some info about water
                # (TODO: bug for testing. Need to restrict period - or we will have outdated info)
                return True
            if already_saved_info.created_at.month == address_info.created_at.month:
                # in pg already saved actual information about water params for this month
                return True
        elif fetched_water_parameters is None:
            return True
    return False

def save_coordinates():
    geocoder_config = read_geocoder_config()

    addresses_of_minsk = get_all_addresses()
    addresses_infos = retrieve_addresses_info(
        addresses_of_minsk,
        geocoder_requests_limit=geocoder_config.requests_limit
    )

    pg_client = PgClient()
    all_addresses_info_in_pg = pg_client.get_all_address_info()
    all_addresses_info_in_pg = {address_info.address: address_info for address_info in  all_addresses_info_in_pg}

    need_to_be_processed = []
    for address_info in tqdm(addresses_infos, desc="Filter address_infos for saving"):
        if need_to_skip_saving(address_info, address_info.water_parameters, all_addresses_info_in_pg):
            continue
        need_to_be_processed.append(address_info)

    for address_info in tqdm(need_to_be_processed, desc="Save coordinates in pg"):
        pg_client.insert_address_info(
            address_info.address,
            address_info.coordinates,
            address_info.water_parameters
        )

def save_water_parameters(all_addresses_infos: list[AddressInfo]):
    config: WaterConfig = read_water_config()
    batched = list(mit.chunked(all_addresses_infos, config.chunk_request_size))
    random.shuffle(batched)

    pg_client = PgClient()
    all_addresses_info_in_pg = pg_client.get_all_address_info()
    all_addresses_info_in_pg = {address_info.address: address_info for address_info in  all_addresses_info_in_pg}

    for idx, addresses_infos in enumerate(batched):
        already_processed_count = idx * config.chunk_request_size
        logging.info(f"Address progress: {already_processed_count}/{len(all_addresses_infos)}")

        chunk_size = config.chunk_request_size
        if already_processed_count + config.chunk_request_size > config.daily_requests_limit:
            chunk_size = config.daily_requests_limit - already_processed_count
            addresses_infos = addresses_infos[:chunk_size]

        water_parameters = retrieve_water_parameters(addresses_infos)
        assert len(addresses_infos) == len(water_parameters)

        # Скорее всего тоже уперлись в лимиты геокодирования
        if count_consecutive_none(water_parameters) > config.daily_consecutive_empty_responses_threshold:
            break

        need_to_be_processed = []
        for address_info, fetched_water_parameters in tqdm(zip(addresses_infos, water_parameters), desc="Filter address_infos for saving"):
            if need_to_skip_saving(address_info, fetched_water_parameters, all_addresses_info_in_pg):
                continue
            need_to_be_processed.append((address_info, fetched_water_parameters))

        for address_info, fetched_water_parameters in tqdm(need_to_be_processed, desc="Save coordinates and water parameters in pg"):
            pg_client.insert_address_info(
                address_info.address,
                address_info.coordinates,
                fetched_water_parameters
            )

        # Уперлись в ежедневные лимиты для водоканала
        if chunk_size != config.chunk_request_size:
            break


def save_coordinates_and_water_parameters():
    geocoder_config = read_geocoder_config()

    addresses_of_minsk = get_all_addresses()
    all_addresses_infos = retrieve_addresses_info(
        addresses_of_minsk,
        geocoder_requests_limit=geocoder_config.requests_limit
    )
    save_water_parameters(all_addresses_infos)



def save_aggregated_hexagons_information():
    pg_client = PgClient()
    all_addresses_info = pg_client.get_all_address_info()
    avg_water_parameters_by_hexagon = compute_avg_parameters_by_hexagons(all_addresses_info)

    pg_client = PgClient()
    for hex_id, avg_water_param in tqdm(avg_water_parameters_by_hexagon.items(), desc="Save hexagons info in pg"):
        pg_client.insert_hexagon(
            hex_id,
            determine_color(avg_water_param),
            avg_water_param
        )

def calculate_water_parameters_task():
    save_coordinates_and_water_parameters()
    # save_aggregated_hexagons_information()


