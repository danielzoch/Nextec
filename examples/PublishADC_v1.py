###!/usr/bin/env python
import cayenne.client
import time
import logging
#ADC Library
import rcpy
import rcpy.adc as adc

# Cayenne authentication info. This should be obtained from the Cayenne Dashboard.
MQTT_USERNAME  = "51276c10-4aa8-11e9-a98b-69b394a1794b"
MQTT_PASSWORD  = "867fec5c9a1c7e7453999e791d1a16526d2f442f"
MQTT_CLIENT_ID = "dca57f90-54dd-11e9-bd24-d78d0eb46731"


client = cayenne.client.CayenneMQTTClient()
client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, loglevel=logging.INFO)
# For a secure connection use port 8883 when calling client.begin:
# client.begin(MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, port=8883, loglevel=logging.INFO)

#Conversion  Coefficient
VoltConv = 100/3
#Incrementing int
k=0
timestamp = 0

while True:
    client.loop()

    if (time.time() > timestamp + 5):
        #Read Raw Value from ADC
        raw = adc.get_raw(0)
        #Read Voltage Value from ADC
        voltage = adc.get_voltage(0)
        #Read Voltage from DC_Jack
        JackVoltage = adc.dc_jack.get_voltage()

	#Converted Voltage Value for Cayenne
        if (JackVoltage < 9):
            Battery_Percentage = 0
        else:
            Battery_Percentage = VoltConv*(JackVoltage-9)

        if (k == 0):
            k = 1
        else:
            k = 0

        #print ("    The ADC Raw Value is: ", raw)
        #print ("    The ADC Voltage is: ", voltage)
        print ("    The Charging Status is: ", k)
        print ("    The Jack Voltage Value is: ", JackVoltage)
        print ("    The Cayenne Battery Level Value is: ", Battery_Percentage)
       # client.celsiusWrite(1, i)
       # client.luxWrite(2, i*10)
       # client.hectoPascalWrite(4, i+800)

        client.virtualWrite(0, k, dataType="prox", dataUnit="d")
        client.virtualWrite(1, Battery_Percentage, dataType="batt", dataUnit="p")
        #client.virtualWrite(3, k)
        timestamp = time.time()

