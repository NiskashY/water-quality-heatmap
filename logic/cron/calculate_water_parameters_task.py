from tqdm import tqdm

from external.pg.client import PgClient
from external.web.ato.client import get_all_addresses
from external.config.yandex_configs import read_geocoder_config

from logic.geo.houses import retrieve_address_info
from logic.water_quality.color import determine_color
from logic.water_quality.water_parameters import retrieve_water_parameters, compute_avg_parameters_by_hexagons

from model.geo import AddressInfo
from model.water_parameters import WaterParameters


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
    addresses_infos = retrieve_address_info(
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

def save_coordinates_and_water_parameters():
    geocoder_config = read_geocoder_config()

    addresses_of_minsk = get_all_addresses()
    addresses_infos = retrieve_address_info(
        addresses_of_minsk,
        geocoder_requests_limit=geocoder_config.requests_limit
    )
    water_parameters = retrieve_water_parameters(addresses_infos)
    assert len(addresses_infos) == len(water_parameters)

    pg_client = PgClient()
    all_addresses_info_in_pg = pg_client.get_all_address_info()
    all_addresses_info_in_pg = {address_info.address: address_info for address_info in  all_addresses_info_in_pg}

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

def save_aggregated_hexagons_information():
    pg_client = PgClient()
    all_addresses_info = pg_client.get_all_address_info()
    avg_water_parameters_by_hexagon = compute_avg_parameters_by_hexagons(all_addresses_info)

    pg_client = PgClient()
    for hex_id, avg_water_param in avg_water_parameters_by_hexagon.items():
        pg_client.insert_hexagon(
            hex_id,
            determine_color(avg_water_param),
            avg_water_param
        )

def calculate_water_parameters_task():
    save_coordinates_and_water_parameters()
    save_aggregated_hexagons_information()


