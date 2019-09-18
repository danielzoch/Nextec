import cayenne.client
import time
import logging

#from time import sleep
import sys
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()


# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "51276c10-4aa8-11e9-a98b-69b394a1794b"
MQTT_PASSWORD  = "867fec5c9a1c7e7453999e791d1a16526d2f442f"
MQTT_CLIENT_ID = "dd059960-54bb-11e9-83b2-37ef83221631"

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)

#timestamp = 0
SCUTTLE_IDs = [248534172589, 623731415800, 919785904744]


while True:
    client.loop()

    print("Hold a tag near the reader")
    id, text = reader.read()
    print("ID: %s\nText: %s" % (id,text))

    n=0
    for x in SCUTTLE_IDs:
        if id == x:
            client.virtualWrite(n, 1, dataType="prox", dataUnit="d")
        else:
            client.virtualWrite(n, 0, dataType="prox", dataUnit="d")
        n=n+1
