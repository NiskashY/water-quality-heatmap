from external.minskvodokanal.client import Client

client = Client()
response = client.v1_request("Леонида Звезды 42")
print(response)
