from external.pg.client import PgClient
from logic.geo.houses import retrieve_houses_with_coordinates
from logic.water_quality.water_parameters import retrieve_water_parameters, compute_avg_parameters_by_hexagons

from external.web.ato.client import get_all_addresses
from external.web.minskvodokanal.client import MinskVodokanalClient
from external.config.yandex_configs import read_geocoder_config


def calculate_water_parameters_task():
    geocoder_config = read_geocoder_config()

    addresses_of_minsk = get_all_addresses()
    addresses_with_coordinates = retrieve_houses_with_coordinates(
        addresses_of_minsk,
        geocoder_requests_limit=geocoder_config.requests_limit
    )[0:10]
    water_parameters = retrieve_water_parameters(addresses_with_coordinates)

    avg_water_parameters_by_hexagon = compute_avg_parameters_by_hexagons(addresses_with_coordinates, water_parameters)
    return avg_water_parameters_by_hexagon
    # pg_client = PgClient()
    # pg_client.save_address_info(addresses_with_coordinates, water_parameters)
    #



