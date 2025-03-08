from smbus2 import SMBus, i2c_msg
from time import sleep

# class REGISTER_ADDRESSES():
#     def __init__(self):
#         self.ADC_I2C_ADDRESS = 0x48

#         self.ADRESS_POINTER_REGISTER = 0

#         self.ADDRESS_POINTER_CONV = 0x00
#         self.ADDRESS_POINTER_CONFIG = 0x01
#         self.ADDRESS_POINTER_LO_THRESH = 0x02
#         self.ADDRESS_POINTER_HI_THRESH = 0x03

#         self.CONFIG_VALUE_MESSAGE_HI_A0 = 0x42
#         self.CONFIG_VALUE_MESSAGE_LO_A0 = 0x83

#         # change input channel between A0 and A1
#         self.CONFIG_VALUE_MESSAGE_HI_A1 = self.CONFIG_VALUE_MESSAGE_HI_A0 ^ 0x10
#         self.CONFIG_VALUE_MESSAGE_LO_A1 = self.CONFIG_VALUE_MESSAGE_LO_A0

ADC_I2C_ADDRESS = 0x48

ADRESS_POINTER_REGISTER = 0

ADDRESS_POINTER_CONV = 0x00
ADDRESS_POINTER_CONFIG = 0x01
ADDRESS_POINTER_LO_THRESH = 0x02
ADDRESS_POINTER_HI_THRESH = 0x03

CONFIG_VALUE_MESSAGE_HI_A0 = 0x42
CONFIG_VALUE_MESSAGE_LO_A0 = 0x83

# change input channel between A0 and A1
CONFIG_VALUE_MESSAGE_HI_A1 = CONFIG_VALUE_MESSAGE_HI_A0 ^ 0x10
CONFIG_VALUE_MESSAGE_LO_A1 = CONFIG_VALUE_MESSAGE_LO_A0

class ADS1115():
    """
    Abstraction class for the adc. Contains methods to configure and read
    soil moisture and rain level sesnors at inputs A0 and A1
    """
    def configure_rain_level_read(self, bus):
        """
        Configures multiplexer to A1 input and configures amplifier
        gain to 1
        
        Args:
            (SMBus) bus: serial bus object
        """
        # Point conversion register to A1 with gain 1
        msg = i2c_msg.write(ADC_I2C_ADDRESS, [ADDRESS_POINTER_CONFIG, CONFIG_VALUE_MESSAGE_HI_A1, CONFIG_VALUE_MESSAGE_LO_A1])
        bus.i2c_rdwr(msg)

    def configure_soil_moisture_read(self, bus):
        """
        Configures multiplexer to A0 input and configures amplifier
        gain to 1
        
        Args:
            (SMBus) bus: serial bus object
        """
        # Point conversion register to A0 with gain 1
        msg = i2c_msg.write(ADC_I2C_ADDRESS, [ADDRESS_POINTER_CONFIG, CONFIG_VALUE_MESSAGE_HI_A0, CONFIG_VALUE_MESSAGE_LO_A0])
        bus.i2c_rdwr(msg)

    def read_adc(self, bus):
        """
        *** only use if configuration register set gain = 1
        
        Args:
            (SMBus) bus: serial bus object
        Returns:
            (int) Voltage at the ADC input
        """
        # point the address to the conversion register
        msg = i2c_msg.write(ADC_I2C_ADDRESS, [ADDRESS_POINTER_CONV])
        bus.i2c_rdwr(msg)
        # read two bits from the bus
        msg = i2c_msg.read(ADC_I2C_ADDRESS, 2)
        bus.i2c_rdwr(msg)

        output_hi = int.from_bytes(msg.buf[0])
        output_lo = int.from_bytes(msg.buf[1])

        # cobine high and low register values
        value = ((output_hi << 8) | output_lo)
        # voltage reading set for configuration gain = 1
        voltage_reading = (float(value)/(2**15))*4.096
        # print("voltag is: " + str(voltage_reading))
        return voltage_reading

    def test_adc(self):
        """
        Test method to check correct ADC functionality
        """
        bus = SMBus(1)
        # config to A0 read opperation with gain 1
        self.configure_soil_moisture_read(bus)
        # adc.configure_rain_level_read()
        while True:
            value = self.read_adc(bus)
            print(value)
            sleep(2)
