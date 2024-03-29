#!/usr/bin/env python
import cayenne.client
import time
import logging

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "51276c10-4aa8-11e9-a98b-69b394a1794b"
MQTT_PASSWORD  = "867fec5c9a1c7e7453999e791d1a16526d2f442f"
MQTT_CLIENT_ID = "2b105410-4e63-11e9-b395-f53190c2ab6f"


client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)

i=0
timestamp = 0

while True:
    client.loop()
    
    if (time.time() > timestamp + 10):
        client.celsiusWrite(1, i)
        client.luxWrite(2, i*10)
        client.hectoPascalWrite(3, i+800)
        timestamp = time.time()
        i = i+1
