from external.minskvodokanal.client import Client
from external.pg.client import PgClient

import logging

logging.basicConfig(level=logging.INFO)

client = Client()
print(client.v1_request("Леонида Звезды 42"))

pg_client = PgClient()
print(pg_client.get_hex("891fb466257ffff"))
