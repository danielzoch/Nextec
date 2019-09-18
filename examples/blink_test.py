# Use the config-pin command line tool to set a pin's function to GPIO
# Then you can control it with the GPIO module from Python
import Adafruit_BBIO.GPIO as GPIO
import time


pin = "GP1_4"

# Set up pins as inputs or outputs
GPIO.setup(pin, GPIO.OUT)  # Alternative: use actual pin names

# Write a logic high or logic low
#GPIO.output(pin, GPIO.HIGH)   # You can also write '0' instead
#time.sleep(15)
# Blinking onboard led example

while True:
	GPIO.output(pin, GPIO.HIGH)
	print("Relays ON")
	time.sleep(10)
	GPIO.output(pin, GPIO.LOW)
	print("Relays OFF")
	time.sleep(10)
