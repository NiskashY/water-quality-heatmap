from external.minskvodokanal.client import Client

import logging

logging.basicConfig(level=logging.INFO)

client = Client()
print(client.v1_request("лвоалова"))
print(client.v1_request("Леонида Звезды 42"))
