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
    hex_id: str
    created_at: datetime
    hex_color: str
    water_parameters: WaterParameters

def make_hex_id(h3_res: int):
    return f'hex_res_{h3_res}_id'