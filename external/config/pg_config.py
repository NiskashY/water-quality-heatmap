# Example of pg.yaml
# pg:
#   dbname: some_db
#   username: some_admin
#   password: some_password

import os, yaml
from dataclasses import dataclass


@dataclass
class PgConfig:
    dbname: str
    username: str
    password: str


def read_pg_config() -> PgConfig:
    def _get_port(port):
        if port is not None:
            return int(port)
        return None

    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{dir_path}/pg.yaml", "r") as stream:
        data_loaded = yaml.safe_load(stream)["pg"]
        return PgConfig(
            dbname=data_loaded["dbname"],
            username=data_loaded["username"],
            password=data_loaded["password"],
        )
