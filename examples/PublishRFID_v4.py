
import cayenne.client
import time
import logging

from time import sleep
import sys
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()


# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "51276c10-4aa8-11e9-a98b-69b394a1794b"
MQTT_PASSWORD  = "867fec5c9a1c7e7453999e791d1a16526d2f442f"
MQTT_CLIENT_ID = "6e351540-d339-11e9-84bb-8f71124cfdfb"

client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)
#Give time to connect before continuing
sleep(2)

#timestamp = 0
SCUTTLE_IDs = [0]
SCUTTLE_STATUS = [0]
id = None

while True:
    client.loop()

    #Save previously read ID into variable
    previous_id = id

    #Scan for RFID tag and Print ID Number
    print("\nHold a tag near the reader")
    id = reader.read_id_NP()
    print("ID: %s" % (id))
    if id == None:
        id = 0


    #Compare Read Tag with SCUTTLE IDs
    n=0
    for x in SCUTTLE_IDs:
        if id == x:
            SCUTTLE_STATUS[n] = 1
        else:
            SCUTTLE_STATUS[n] = 0
        n=n+1

    #Check to see if the Read Tag is not recognized, then add it to the ID array
    sum=0
    for x in SCUTTLE_STATUS:
        sum = sum+x
    if sum == 0:
        SCUTTLE_IDs.append(id)
        SCUTTLE_STATUS.append(1)

    #If Previous Tag does not equal recently Read Tag, then Update Statuses to Cayenne
    n=0
    if id != previous_id:
        for x in SCUTTLE_IDs:
            client.virtualWrite(x, SCUTTLE_STATUS[n], dataType="prox", dataUnit="d")
            n=n+1

    sleep(1.5)
