from external.yandex.geocoder.client import GeocoderClient
from external.pg.client import PgClient
from external.web.minskvodokanal.client import MinskVodokanalClient
from logic.web.retrieve_houses import retrieve_and_dump_addresses_to_file
import logging

logging.basicConfig(level=logging.INFO)

retrieve_and_dump_addresses_to_file()
#
# address = "Республика Беларусь, г. Минск, Газеты Звезды 42"
# hex_res = 9
#
# client = GeocoderClient()
#
# coordinates = client.coordinates(address)
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
