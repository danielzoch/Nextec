import time
import paho.mqtt.client as mqtt
from cayenne import __version__


# Data types
TYPE_ACCELERATION = 'accel' # Acceleration, units: UNIT_G
TYPE_ANALOG_ACTUATOR = 'analog_actuator' # Analog Actuator, units: UNIT_ANALOG
TYPE_ANALOG_SENSOR = 'analog_sensor' # Analog Sensor, units: UNIT_ANALOG
TYPE_BAROMETRIC_PRESSURE = 'bp' # Barometric pressure, units: UNIT_PASCAL, UNIT_HECTOPASCAL
TYPE_BATTERY = 'batt' # Battery, units: UNIT_PERCENT, UNIT_RATIO, UNIT_VOLTS
TYPE_CO2 = 'co2' # Carbon Dioxide, units: UNIT_PPM
TYPE_COUNTER = 'counter' # Counter, units: UNIT_ANALOG
TYPE_CURRENT = 'current' # Current, units: UNIT_AMP, UNIT_MAMP
TYPE_DIGITAL_ACTUATOR = 'digital_actuator' # Digital Actuator, units: UNIT_DIGITAL
TYPE_DIGITAL_SENSOR = 'digital_sensor' # Digital Sensor, units: UNIT_DIGITAL
TYPE_ENERGY = 'energy' # Energy, units: UNIT_KWH
TYPE_EXT_WATERLEAK = 'ext_wleak' # External Waterleak, units: UNIT_ANALOG
TYPE_FREQUENCY = 'freq' # Frequency, units: UNIT_HERTZ
TYPE_GPS = 'gps' # GPS, units: UNIT_GPS
TYPE_GYROSCOPE = 'gyro' # Gyroscope, units: UNIT_ROTATION_PER_MINUTE, UNIT_DEGREE_PER_SEC
TYPE_LUMINOSITY = 'lum' # Luminosity, units: UNIT_LUX, UNIT_VOLTS, UNIT_PERCENT, UNIT_RATIO
TYPE_MOTION = 'motion' # Motion, units: UNIT_DIGITAL
TYPE_POWER = 'pow' # Power, units: UNIT_WATT, UNIT_KILOWATT
TYPE_PROXIMITY = 'prox' # Proximity, units: UNIT_CENTIMETER, UNIT_METER, UNIT_DIGITAL
TYPE_RAIN_LEVEL = 'rain_level' # Rain Level, units: UNIT_CENTIMETER, UNIT_MILLIMETER
TYPE_RELATIVE_HUMIDITY = 'rel_hum' # Relative Humidity, units: UNIT_PERCENT, UNIT_RATIO
TYPE_RESISTANCE = 'res' # Resistance, units: UNIT_OHM
TYPE_RSSI = 'rssi' # Received signal strength indicator, units: UNIT_DBM
TYPE_SNR = 'snr' # Signal Noise Ratio, units: UNIT_DB
TYPE_SOIL_MOISTURE = 'soil_moist' # Soil Moisture, units: UNIT_PERCENT
TYPE_SOIL_PH = 'soil_ph' # Soil pH, units: UNIT_ANALOG
TYPE_SOIL_WATER_TENSION = 'soil_w_ten' # Soil Water Tension, units: UNIT_KILOPASCAL, UNIT_PASCAL
TYPE_TANK_LEVEL = 'tl' # Tank Level, units: UNIT_ANALOG
TYPE_TEMPERATURE = 'temp' # Temperature, units: UNIT_FAHRENHEIT, UNIT_CELSIUS, UNIT_KELVIN
TYPE_VOLTAGE = 'voltage' # Voltage, units: UNIT_VOLTS, UNIT_MILLIVOLTS
TYPE_WIND_SPEED = 'wind_speed' # Wind Speed, units: UNIT_KM_PER_H

# Unit types
UNIT_UNDEFINED = 'null' # Undefined unit type
UNIT_AMP = 'a' # Ampere
UNIT_ANALOG = 'null' # Analog
UNIT_CELSIUS = 'c' # Celsius
UNIT_CENTIMETER = 'cm' # Centimeter
UNIT_DB = 'db' # Decibels
UNIT_DBM = 'dbm' # dBm
UNIT_DEGREE_PER_SEC = 'dps' # Degree per second
UNIT_DIGITAL = 'd' # Digital (0/1)
UNIT_FAHRENHEIT = 'f' # Fahrenheit
UNIT_G = 'g' # Acceleration
UNIT_GPS = 'm' # GPS
UNIT_HECTOPASCAL = 'hpa' # Hectopascal
UNIT_HERTZ = 'hz' # Hertz
UNIT_KELVIN = 'k' # Kelvin
UNIT_KILOPASCAL = 'kpa' # Kilopascal
UNIT_KILOWATT = 'kw' # Kilowatts
UNIT_KM_PER_H = 'kmh' # Kilometer per hour
UNIT_KWH = 'kwh' # Killowatt Hour
UNIT_LUX = 'lux' # Lux
UNIT_MAMP = 'ma' # Milliampere
UNIT_METER = 'm' # Meter
UNIT_MILLIMETER = 'mm' # Millimeter
UNIT_MILLIVOLTS = 'mv' # Millivolts
UNIT_OHM = 'ohm' # Ohm
UNIT_PASCAL = 'pa' # Pascal
UNIT_PERCENT = 'p' # Percent (%)
UNIT_PPM = 'ppm' # Parts per million
UNIT_RATIO = 'r' # Ratio
UNIT_ROTATION_PER_MINUTE = 'rpm' # Rotation per minute
UNIT_VOLTS = 'v' # Volts
UNIT_WATT = 'w' # Watts

# Topics
COMMAND_TOPIC = "cmd"
DATA_TOPIC = "data"
RESPONSE_TOPIC = "response"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, cayenne, flags, rc):
    if rc != 0:
        # MQTT broker error codes
        broker_errors = {
            1 : 'unacceptable protocol version',
            2 : 'identifier rejected',
            3 : 'server unavailable',
            4 : 'bad user name or password',
            5 : 'not authorized',
        }
        error = "Connection failed, " + broker_errors.get(rc, "result code " + str(rc))
        raise Exception(error)
    else:
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        cayenne.connected = True
        cayenne.reconnect = False
        command_topic = cayenne.getCommandTopic()
        print("SUB %s\n" % command_topic)
        client.subscribe(command_topic)
        cayenne.mqttPublish("%s/sys/model" % cayenne.rootTopic, "Python")
        cayenne.mqttPublish("%s/sys/version" % cayenne.rootTopic, __version__)

# The callback for when the client disconnects from the server.
def on_disconnect(client, cayenne, rc):
    print("Disconnected with result code "+str(rc))
    cayenne.connected = False
    cayenne.reconnect = True
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, cayenne, msg):
    print(msg.topic+" "+str(msg.payload))
    if cayenne.on_message:
        message = CayenneMessage(msg)
        error = cayenne.on_message(message)
        if not error:
            # If there was no error, we send the new channel state, which should be the command value we received.
            cayenne.virtualWrite(message.channel, message.value)
        # Send a response showing we received the message, along with any error from processing it.
        cayenne.responseWrite(message.msg_id, error)
        
class CayenneMessage:
    """ This is a class that describes an incoming Cayenne message. It is
    passed to the on_message callback as the message parameter.

    Members:

    client_id : String. Client ID that the message was published on.
    topic : String. Topic that the message was published on.
    channel : Int. Channel that the message was published on.
    msg_id : String. The message ID.
    value : String. The message value.
    """
    def __init__(self, msg):
        topic_tokens = msg.topic.split('/')
        self.client_id = topic_tokens[3]
        self.topic = topic_tokens[4]
        self.channel = int(topic_tokens[5])
        if msg.payload is str:
            payload_tokens = msg.payload.split(',')
        else:
            payload_tokens = msg.payload.decode().split(',')
        self.msg_id = payload_tokens[0]
        self.value = payload_tokens[1]
        
    def __repr__(self):
        return str(self.__dict__)
        
class CayenneMQTTClient:
    """Cayenne MQTT Client class.
    
    This is the main client class for connecting to Cayenne and sending and receiving data.
    
    Standard usage:
    * Set on_message callback, if you are receiving data.
    * Connect to Cayenne using the begin() function.
    * Call loop() at intervals (or loop_forever() once) to perform message processing.
    * Send data to Cayenne using write functions: virtualWrite(), celsiusWrite(), etc.
    * Receive and process data from Cayenne in the on_message callback.

    The on_message callback can be used by creating a function and assigning it to CayenneMQTTClient.on_message member.
    The callback function should have the following signature: on_message(message)
    The message variable passed to the callback is an instance of the CayenneMessage class.
    """
    client = None
    rootTopic = ""
    connected = False
    reconnect = False
    on_message = None
    
    def begin(self, username, password, clientid, hostname='mqtt.mydevices.com', port=1883):
        """Initializes the client and connects to Cayenne.
        
        username is the Cayenne username.
        password is the Cayenne password.
        clientID is the Cayennne client ID for the device.
        hostname is the MQTT broker hostname.
        port is the MQTT broker port.
        """
        self.rootTopic = "v1/%s/things/%s" % (username, clientid)
        self.client = mqtt.Client(client_id=clientid, clean_session=True, userdata=self)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.username_pw_set(username, password)
        self.client.connect(hostname, port, 60)        
        print("Connecting to %s..." % hostname)

    def loop(self):
        """Process Cayenne messages.
        
        This should be called regularly to ensure Cayenne messages are sent and received.
        """
        self.client.loop()
        if not self.connected and self.reconnect:
            try:
                self.client.reconnect()
                self.reconnect = False
            except:
                print("Reconnect failed, retrying")
                time.sleep(5)
    
    def loop_forever(self):
        """Process Cayenne messages in a blocking loop that runs forever."""
        self.client.loop_forever()
    
    def getDataTopic(self, channel):
        """Get the data topic string.
        
        channel is the channel to send data to.
        """
        return "%s/%s/%s" % (self.rootTopic, DATA_TOPIC, channel)
    
    def getCommandTopic(self):
        """Get the command topic string."""
        return "%s/%s/+" % (self.rootTopic, COMMAND_TOPIC)

    def getResponseTopic(self):
        """Get the response topic string."""
        return "%s/%s" % (self.rootTopic, RESPONSE_TOPIC)

    def virtualWrite(self, channel, value, dataType="", dataUnit=""):
        """Send data to Cayenne.
        
        channel is the Cayenne channel to use.
        value is the data value to send.
        dataType is the type of data.
        dataUnit is the unit of the data.
        """
        if (self.connected):
            topic = self.getDataTopic(channel)
            if dataType:
                payload = "%s,%s=%s" % (dataType, dataUnit, value)
            else:
                payload = value
            self.mqttPublish(topic, payload)

    def responseWrite(self, msg_id, error_message):
        """Send a command response to Cayenne.
        
        This should be sent when a command message has been received.
        msg_id is the ID of the message received.
        error_message is the error message to send. This should be set to None if there is no error.
        """
        if (self.connected):
            topic = self.getResponseTopic()
            if error_message:
                payload = "error,%s=%s" % (msg_id, error_message)
            else:
                payload = "ok,%s" % (msg_id)
            self.mqttPublish(topic, payload)            
            
    def celsiusWrite(self, channel, value):
        """Send a Celsius value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_TEMPERATURE, UNIT_CELSIUS)

    def fahrenheitWrite(self, channel, value):
        """Send a Fahrenheit value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_TEMPERATURE, UNIT_FAHRENHEIT)

    def kelvinWrite(self, channel, value):
        """Send a kelvin value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_TEMPERATURE, UNIT_KELVIN)
    
    def luxWrite(self, channel, value):
        """Send a lux value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_LUMINOSITY, UNIT_LUX)
    
    def pascalWrite(self, channel, value):
        """Send a pascal value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_BAROMETRIC_PRESSURE, UNIT_PASCAL)
    
    def hectoPascalWrite(self, channel, value):
        """Send a hectopascal value to Cayenne.

        channel is the Cayenne channel to use.
        value is the data value to send.
        """
        self.virtualWrite(channel, value, TYPE_BAROMETRIC_PRESSURE, UNIT_HECTOPASCAL)

    def accelWrite(self, channel, x=UNIT_UNDEFINED, y=UNIT_UNDEFINED, z=UNIT_UNDEFINED):
        """Send an acceleration value list to Cayenne.

        channel is the Cayenne channel to use.
        x is the acceleration on the X-axis.
        y is the acceleration on the Y-axis.
        z is the acceleration on the Z-axis.
        """
        value = [x, y, z]
        value = ''.join(c for c in repr(value) if c not in (" ", "'"))
        self.virtualWrite(channel, value, TYPE_ACCELERATION, UNIT_G)

    def gpsWrite(self, channel, latitude=UNIT_UNDEFINED, longitude=UNIT_UNDEFINED, altitude=UNIT_UNDEFINED):
        """Send a GPS value list to Cayenne.

        channel is the Cayenne channel to use.
        latitude is the latitude in degrees.
        longitude is the longitude in degrees.
        altitude is the altitude in meters.
        """
        value = [latitude, longitude, altitude]
        value = ''.join(c for c in repr(value) if c not in (" ", "'"))
        self.virtualWrite(channel, value, TYPE_GPS, UNIT_METER)

    def mqttPublish(self, topic, payload):
        """Publish a payload to a topic
        
        topic is the topic string.
        payload is the payload data.
        """
        print("PUB %s\n%s\n" % (topic, payload))
        self.client.publish(topic, payload, 0, False)    
