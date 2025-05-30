import json
import logging
import time

import schedule
from flask import Flask, jsonify
from flask_cors import CORS

from external.config.geo_config import GeoConfig, read_geo_config
from external.pg.client import PgClient
from external.web.ato.client import save_addresses
from external.web.minskvodokanal.client import MinskVodokanalClient
from logic.cron.calculate_water_parameters_task import save_coordinates_and_water_parameters
from logic.geo.houses import retrieve_address_info
from logic.water_quality.water_parameters import retrieve_water_parameters
from model.geo import Hexagon, GeoEncoder

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    format='%(levelname)s:%(name)s - [%(asctime)s] "%(message)s"',
    datefmt='%d/%b/%Y %H:%M:%S',  # Формат даты как у Werkzeug
    level=logging.INFO,
)

@app.route("/v1/hexagon/all/<int:hex_res>/colors", methods=["GET"])
def get_hexagons_with_colors(hex_res: int):
    pg_client = PgClient()
    all_hexagons: list[Hexagon] = pg_client.get_all_hexes_with_res(hex_res)
    hexagons_with_colors: list[tuple[str, tuple[int, int, int]]] = [(hexagon.hex_id, hexagon.hex_color) for hexagon in all_hexagons]
    return hexagons_with_colors

@app.route("/v1/hexagon/all/<int:hex_res>/info", methods=["GET"])
def get_hexagons_info(hex_res: int):
    pg_client = PgClient()
    all_hexagons: list[Hexagon] = pg_client.get_all_hexes_with_res(hex_res)
    return all_hexagons

@app.route("/v1/hexagon/<hex_id>/info", methods=["GET"])
def get_hexagon_info(hex_id: str):
    pg_client = PgClient()
    hexagon = pg_client.get_info_about_hex(hex_id)
    return json.dumps(hexagon, cls=GeoEncoder, ensure_ascii=False)

@app.route("/v1/address/<address>/water", methods=["GET"])
def get_address_water(address: str):
    client = MinskVodokanalClient()
    water_parameters = client.v1_request(address)
    return json.dumps(water_parameters, cls=GeoEncoder, ensure_ascii=False)

@app.route("/v1/address/<address>/info", methods=["GET"])
def get_address_info(address: str):
    address_info = retrieve_address_info(address)
    if address_info:
        if address_info.water_parameters is None:
            address_info.water_parameters = retrieve_water_parameters([address_info])[0]
            pg_client = PgClient()
            pg_client.insert_address_info(
                address_info.address,
                address_info.coordinates,
                address_info.water_parameters
            )

    return json.dumps(address_info, cls=GeoEncoder, ensure_ascii=False)


@app.route("/v1/hexagon/available_resolutions", methods=["GET"])
def get_get_available_resolutions():
    geo_config = read_geo_config()
    return geo_config.allowed_hexagons_resolutions