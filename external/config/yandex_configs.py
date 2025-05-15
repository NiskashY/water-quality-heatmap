# Example of yandex.yaml
# yandex:
#   geocoder:
#     api_key: "<YOUR_API_KEY>"
#     requests_limit: 0
#     chunk_request_size: 10
import os, yaml
from dataclasses import dataclass


@dataclass
class GeocoderConfig:
    api_key: str
    requests_limit: int
    chunk_request_size: int

def read_geocoder_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/yandex.yaml", "r") as stream:
        data_loaded = yaml.safe_load(stream)["yandex"]["geocoder"]
        return GeocoderConfig(
            api_key=data_loaded["api_key"],
            requests_limit=int(data_loaded["requests_limit"]),
            chunk_request_size=int(data_loaded["chunk_request_size"]),
        )
