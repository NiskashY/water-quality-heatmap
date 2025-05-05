import logging


from external.yandex.geocoder.client import GeocoderClient
from external.pg.client import PgClient
from external.web.minskvodokanal.client import MinskVodokanalClient
from logic.web.houses import dump_addresses_to_file, read_already_fetched_houses, enrich_with_hexagons, retrieve_houses

logging.basicConfig(level=logging.INFO)

def test_enrich_and_print():
    def enrich_and_print(addresses_and_coordinates, hex_res):
        enriched = enrich_with_hexagons(addresses_and_coordinates, hex_res)

        unique_hex_ids = {obj['hex_id'] for obj in enriched}
        print(f'\nUnique hexes (len = {len(unique_hex_ids)})')
        for hex_id in unique_hex_ids:
            print(f'\t{hex_id}')


    houses = read_already_fetched_houses()
    print(houses)
    print( f'Total houses = {len(houses)}')
    enrich_and_print(houses, 9)
    enrich_and_print(houses, 8)
    enrich_and_print(houses, 7)
    enrich_and_print(houses, 6)

def enrich_and_save():
    houses = retrieve_houses()
    dump_addresses_to_file(houses)

if __name__ == "__main__":
    enrich_and_save()

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
