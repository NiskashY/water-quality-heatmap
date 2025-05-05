import copy

import h3
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from external.web.minskvodokanal.client import MinskVodokanalClient
from model.geo import make_hex_id, Point
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

def retrieve_water_parameters(addresses: list[str]) -> list[WaterParameters]:
    client = MinskVodokanalClient()
    with logging_redirect_tqdm():
        res = [client.v1_request(address_and_coordinates['address']) for address_and_coordinates in tqdm(addresses)]
        print(res)
        return res

def compute_avg_parameters_by_hexagons(addresses_with_coordinates, water_parameters: list[WaterParameters]):
    geo_config: GeoConfig = read_geo_config()

    hex_id_to_list_of_water_parameters_map = {}
    for hex_res in geo_config.allowed_hexagons_resolutions:
        for address_obj, water_params in zip(addresses_with_coordinates, water_parameters):
            lat, lon = address_obj['coordinates']['latitude'], address_obj['coordinates']['longitude']

            hex_id = h3.latlng_to_cell(lat, lon, hex_res)
            if hex_id in hex_id_to_list_of_water_parameters_map:
                hex_id_to_list_of_water_parameters_map[hex_id].append(water_params)
            else:
                hex_id_to_list_of_water_parameters_map[hex_id] = [water_params]

    hex_id_to_avg_water_parameters = {}
    for hex_id, list_of_water_params in hex_id_to_list_of_water_parameters_map.items():
        avg_wp = _compute_avg_water_parameters(list_of_water_params)
        hex_id_to_avg_water_parameters[hex_id] = avg_wp

        # print(f'\thex_id = {hex_id}')
        # for wp in list_of_water_params:
        #     print(f'\t\t{wp}')
        # print(f'\t\tAVG = {avg_wp}')

    return hex_id_to_avg_water_parameters