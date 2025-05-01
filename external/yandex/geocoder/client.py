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
    def hexagon(self, address: str):
        geo_point = self.coordinates(address)
        # h3.latlng_to_cell(geo)
        pass
