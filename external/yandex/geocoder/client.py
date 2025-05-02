# pip install yandex-geocoder
# pip install h3
from decimal import Decimal

from yandex_geocoder import Client
from external.config.yandex_configs import GeocoderConfig, read_geocoder_config
from model.geo import Point
import h3


class GeocoderClient:
    __config: GeocoderConfig = read_geocoder_config()
    __geocoder_client = Client(__config.api_key)

    def coordinates(self, address: str):
        lon, lat = self.__geocoder_client.coordinates(address)
        return Point(
            latitude=float(lat),
            longitude=float(lon),
        )

    def address(self, point: Point):
        return self.__geocoder_client.address(
            Decimal(point.longitude), Decimal(point.latitude)
        )

    # convert with h3 library
    def hexagon(self, address: str, hex_resolution: int):
        geo_point = self.coordinates(address)
        return h3.latlng_to_cell(
            geo_point.latitude, geo_point.longitude, hex_resolution
        )

    def hexagon_to_nearby_house(self, h3_cell: str):
        lat, lon = h3.cell_to_latlng(h3_cell)
        return self.address(Point(latitude=lat, longitude=lon))
