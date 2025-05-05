from dataclasses import dataclass
from datetime import datetime
from json import JSONEncoder

from model.water_parameters import WaterParameters


@dataclass
class Point:
    latitude: float
    longitude: float

class GeoPointEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

@dataclass
class Hexagon:
    created_at: datetime
    hex_id: str
    hex_resolution: int
    hex_color: tuple[int, int, int]
    avg_water_parameters: WaterParameters

@dataclass
class AddressInfo:
    created_at: datetime
    address: str
    coordinates: Point
    water_parameters: WaterParameters


def make_hex_id(h3_res: int):
    return f'hex_res_{h3_res}_id'