# Example of water_config.yaml
# minskvodokanal:
#     daily_requests_limit: 100
#     chunk_request_size: 10
import os, yaml
from dataclasses import dataclass


@dataclass
class WaterConfig:
    daily_requests_limit: int
    daily_consecutive_empty_responses_threshold: int
    chunk_request_size: int

def read_water_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/water_config.yaml", "r") as stream:
        data_loaded = yaml.safe_load(stream)["minskvodokanal"]
        return WaterConfig(
            daily_requests_limit=data_loaded["daily_requests_limit"],
            daily_consecutive_empty_responses_threshold=data_loaded["daily_consecutive_empty_responses_threshold"],
            chunk_request_size=int(data_loaded["chunk_request_size"]),
        )
