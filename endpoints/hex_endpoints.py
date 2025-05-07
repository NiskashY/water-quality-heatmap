import json

from flask import Flask, jsonify

from external.pg.client import PgClient
from model.geo import Hexagon, GeoEncoder

app = Flask(__name__)

@app.route("/v1/hexagon/all/<int:hex_res>/colors", methods=["GET"])
def get_hexagons_with_colors(hex_res: int):
    pg_client = PgClient()
    all_hexagons: list[Hexagon] = pg_client.get_all_hexes_with_res(hex_res)
    hexagons_with_colors: list[tuple[str, tuple[int, int, int]]] = [(hexagon.hex_id, hexagon.hex_color) for hexagon in all_hexagons]
    return hexagons_with_colors

@app.route("/v1/hexagon/<hex_id>/info", methods=["GET"])
def get_hexagon_info(hex_id: str):
    pg_client = PgClient()
    hexagon = pg_client.get_info_about_hex(hex_id)
    return json.dumps(hexagon, cls=GeoEncoder, ensure_ascii=False)
