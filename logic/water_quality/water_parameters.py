import copy
import datetime
import logging
from collections import defaultdict
from typing import Dict

import h3
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from external.pg.client import PgClient
from external.web.minskvodokanal.client import MinskVodokanalClient
from logic.water_quality.color import determine_color
from model.geo import make_hex_id, Point, AddressInfo
from model.water_parameters import WaterParameters, Parameter

from external.config.geo_config import read_geo_config, GeoConfig

def _compute_avg_water_parameters(in_list_of_water_parameters: list[WaterParameters]) -> WaterParameters | None:
    def avg(lst):
        return sum(lst) / len(lst)

    list_of_water_parameters = list(filter(lambda x: x is not None, in_list_of_water_parameters))
    if list_of_water_parameters:
        avg_water_params = copy.deepcopy(list_of_water_parameters[0])
        avg_water_params.smell.value = avg([param.smell.value for param in list_of_water_parameters])
        avg_water_params.taste.value = avg([param.taste.value for param in list_of_water_parameters])
        avg_water_params.color.value = avg([param.color.value for param in list_of_water_parameters])
        avg_water_params.muddiness.value = avg([param.muddiness.value for param in list_of_water_parameters])
        avg_water_params.general_mineralization.value = avg([param.general_mineralization.value for param in list_of_water_parameters])

        return avg_water_params
    return None

def _log_debug_info(
    hex_id: str,
    water_params: list[WaterParameters],
    avg_wp: WaterParameters
) -> None:
    logging.debug(f'\thex_id = {hex_id}')
    for wp in water_params:
        logging.debug(f'\t\t{wp}')
    logging.debug(f'\t\tAVG = {avg_wp}')
    logging.debug(f'\t\tcolor = rgb{determine_color(avg_wp)}')

def compute_avg_parameters_by_hexagons(addresses_infos: list[AddressInfo]):
    geo_config: GeoConfig = read_geo_config()

    with logging_redirect_tqdm():
        hex_id_to_water_params: Dict[str, list[WaterParameters]] = defaultdict(list)
        for hex_res in geo_config.allowed_hexagons_resolutions:
            for address_info in tqdm(addresses_infos, desc=f"Group coordinates to hexagons with hex_res={hex_res}"):
                hex_id = h3.latlng_to_cell(
                    address_info.coordinates.latitude,
                    address_info.coordinates.longitude,
                    hex_res
                )
                if hex_id not in hex_id_to_water_params:
                    hex_id_to_water_params[hex_id] = []
                if address_info.water_parameters:
                    hex_id_to_water_params[hex_id].append(address_info.water_parameters)

        hex_id_to_avg_water_parameters = {}
        for hex_id, list_of_water_params in tqdm(hex_id_to_water_params.items(), desc=f"Calculate avg parameters for hexagons"):
            avg_wp = _compute_avg_water_parameters(list_of_water_params)
            hex_id_to_avg_water_parameters[hex_id] = avg_wp
            _log_debug_info(hex_id, list_of_water_params, avg_wp)

        return hex_id_to_avg_water_parameters

def retrieve_water_parameters(addresses_infos: list[AddressInfo]) -> list[WaterParameters]:
    client = MinskVodokanalClient()
    with logging_redirect_tqdm():
        def get_amount_of_days(created_at):
            diff = datetime.datetime.now() - created_at
            return diff.days

        def predicate(x: AddressInfo):
            return x.water_parameters is None \
                # and get_amount_of_days(x.created_at) > 0
        def negative_predicate(x: AddressInfo):
            return not predicate(x)

        not_fetched_water_parameters = list(filter(predicate, addresses_infos))
        already_fetched_water_parameters = list(filter(negative_predicate, addresses_infos))
        already_fetched_water_parameters = [addr.water_parameters for addr in already_fetched_water_parameters]
        for address_info in tqdm(not_fetched_water_parameters, "Fetch water parameters from minskvodokanal.by"):
            already_fetched_water_parameters.append(client.v1_request(address_info.address))
        return already_fetched_water_parameters
