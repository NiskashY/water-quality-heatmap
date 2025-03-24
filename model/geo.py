from dataclasses import dataclass
from datetime import datetime

from model.water_parameters import WaterParameters


@dataclass
class Point:
    latitude: float
    longitude: float


@dataclass
class Hexagon:
    hex_id: str
    created_at: datetime
    hex_color: str
    water_parameters: WaterParameters
