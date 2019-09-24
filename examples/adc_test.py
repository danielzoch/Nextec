import time
import rcpy
import rcpy.adc as adc



while True:
    JackVoltage = adc.dc_jack.get_voltage()
    print ("    The Jack Voltage Value is: ", JackVoltage)
    time.sleep(1.5)

