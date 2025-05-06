from dataclasses import dataclass, is_dataclass, asdict
from datetime import datetime
from json import JSONEncoder, JSONDecoder
from typing import Optional, Any, Dict

from model.water_parameters import WaterParameters, Parameter


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
    avg_water_parameters: Optional[WaterParameters]

@dataclass
class AddressInfo:
    created_at: datetime
    address: str
    coordinates: Point
    water_parameters: Optional[WaterParameters]

class AddressInfoEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            # формат ПГ
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')

        if is_dataclass(obj):
            result = asdict(obj)
            if hasattr(obj, 'norm'):
                result['norm'] = obj.norm()
            return result

        return super().default(obj)

class AddressInfoDecoder(JSONDecoder):
    def default(dct: Dict[str, Any]) -> Any:
        if all(k in dct for k in ('latitude', 'longitude')):
            return Point(**dct)

        if all(k in dct for k in ('name', 'units', 'value', 'max_allowed_concentration')):
            return Parameter(**{k: v for k, v in dct.items()
                                if k in ('name', 'units', 'value', 'max_allowed_concentration')})

        if all(k in dct for k in ('smell', 'taste', 'color', 'muddiness', 'general_mineralization')):
            return WaterParameters(**dct)

        if 'created_at' in dct and 'address' in dct and 'coordinates' in dct:
            return AddressInfo(**dct)
        if 'address' in dct and 'coordinates' in dct:
            return AddressInfo(created_at=datetime.now(), water_parameters=None, **dct)

        return dct

def make_hex_id(h3_res: int):
    return f'hex_res_{h3_res}_id'