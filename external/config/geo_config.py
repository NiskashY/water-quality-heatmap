# Example of geo_config.yaml
# map_settings:
#   allowed_hexagons_resolutions:
#     - 7
#     - 8

import os, yaml
from dataclasses import dataclass


@dataclass
class GeoConfig:
    allowed_hexagons_resolutions: list[int]


def read_geo_config() -> GeoConfig:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/geo.yaml", "r") as stream:
        data_loaded = yaml.safe_load(stream)["map_settings"]
        return GeoConfig(
            allowed_hexagons_resolutions=data_loaded["allowed_hexagons_resolutions"],
        )


# def test_read_geo_config():
#     cfg = read_geo_config()
#     assert cfg.allowed_hexagons_resolutions == [7, 8]
#
# test_read_geo_config()