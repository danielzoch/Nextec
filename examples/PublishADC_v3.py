###!/usr/bin/env python
import cayenne.client
import time
import logging
from time import sleep
#ADC Library
import rcpy
import rcpy.adc as adc
#GPIO Library
import Adafruit_BBIO.GPIO as GPIO

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
#Initialize Voltages, timestamp, and GPIO pin
Previous_Volt = 0
JackVoltage = 0
timestamp = 0
GPIO_pin = "GP1_4"

#Setup GPIO pin as an OUTPUT
GPIO.setup(GPIO_pin, GPIO.OUT)

print("Evaluating current voltage readings...")
JackVoltage = adc.dc_jack.get_voltage()




while True:
    client.loop()
    #Continue if 5 seconds has passed
    if (time.time() > timestamp + 5):
        #Check if SCUTTLE is charging
        if Previous_Volt > JackVoltage+0.02:
            print("SCUTTLE is charging... toggling relays ON")
            Charging_Status = 1
            Previous_Volt = JackVoltage
            #Toggle Relay ON to get accurate voltage reading while charging
            GPIO.output(GPIO_pin, GPIO.HIGH)
            sleep(0.5)
            JackVoltage = adc.dc_jack.get_voltage()
            #Toggle Relay back OFF
            GPIO.output(GPIO_pin, GPIO.LOW)
            print("Relays OFF")
        else:
            print("SCUTTLE is not charging")
            Charging_Status = 0
            Previous_Volt = JackVoltage
            JackVoltage = adc.dc_jack.get_voltage()


	#Convert Voltage Value to Percentage for Cayenne
        if (JackVoltage < 9):
            Battery_Percentage = 0
        else:
            Battery_Percentage = VoltConv*(JackVoltage-9)


        print ("    The Charging Status is: ", Charging_Status)
        print ("    The Jack Voltage Value is: ", JackVoltage)
        print ("    The Cayenne Battery Level Value is: ", Battery_Percentage)

        #Send Charging Status and Battery Percentage to Cayenne
        client.virtualWrite(0, Charging_Status, dataType="prox", dataUnit="d")
        client.virtualWrite(1, Battery_Percentage, dataType="batt", dataUnit="p")

        timestamp = time.time()

