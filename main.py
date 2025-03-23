from external.minskvodokanal.client import Client

import logging

logging.basicConfig(level=logging.INFO)

client = Client()
response = client.v1_request("Леонида Звезды 42")
print(response)
