import os, yaml
from dataclasses import dataclass


@dataclass
class GeocoderConfig:
    api_key: str
    requests_limit: int


def read_geocoder_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/yandex.yaml", "r") as stream:
        data_loaded = yaml.safe_load(stream)["yandex"]["geocoder"]
        return GeocoderConfig(
            api_key=data_loaded["api_key"],
            requests_limit=int(data_loaded["requests_limit"])
        )
