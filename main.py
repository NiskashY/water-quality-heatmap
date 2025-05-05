import logging

import h3

from external.web.ato.client import get_all_addresses
from external.yandex.geocoder.client import GeocoderClient
from external.pg.client import PgClient
from external.web.minskvodokanal.client import MinskVodokanalClient
from logic.cron.calculate_water_parameters_task import calculate_water_parameters_task
from logic.geo.houses import dump_addresses_to_file, read_already_fetched_houses, enrich_with_hexagons, retrieve_houses_with_coordinates
from logic.water_quality.water_parameters import compute_avg_parameters_by_hexagons
from model.geo import make_hex_id

logging.basicConfig(level=logging.INFO)

def test_enrich_and_print():
    def enrich_and_print(addresses_and_coordinates, hex_res):
        enriched = enrich_with_hexagons(addresses_and_coordinates, hex_res)

        unique_hex_ids = {obj[make_hex_id(hex_res)] for obj in enriched}
        print(f'\nUnique hexes with hex_res = {hex_res} (len = {len(unique_hex_ids)})')
        for hex_id in unique_hex_ids:
            print(f'\t{hex_id}; hex_childrens={h3.cell_to_children(hex_id)}')


    houses = read_already_fetched_houses()
    print(houses)
    print( f'Total houses = {len(houses)}')
    enrich_and_print(houses, 6)
    enrich_and_print(houses, 7)
    # enrich_and_print(houses, 8)
    # enrich_and_print(houses, 9)

def enrich_and_save():
    addresses = get_all_addresses()
    houses = retrieve_houses_with_coordinates(addresses, geocoder_requests_limit=2)
    dump_addresses_to_file(houses)

def test_avg_parameters():
    calculate_water_parameters_task()

if __name__ == "__main__":
    test_avg_parameters()

# h3_cell = client.hexagon(address, hex_res)
# nearby_house = client.hexagon_to_nearby_house(h3_cell)
#
# print(coordinates.latitude, ";", coordinates.longitude)
# print(h3_cell)
# print(nearby_house)
#
# client = MinskVodokanalClient()
# print(client.v1_request("Леонида Звезды 42"))
#
# pg_client = PgClient()
# print(pg_client.get_hex("891fb466257ffff"))
