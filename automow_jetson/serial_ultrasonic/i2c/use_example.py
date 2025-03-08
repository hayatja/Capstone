# run this script to test ultrasonic 
# sensors connection to jetson nano

from smbus2 import SMBus, i2c_msg
import serial_ultrasonic
from time import sleep

ARDUINO_ADDRESS = 11


if __name__ == "__main__":
    # Create an smbus object (you might need to change the bus number)
    bus = SMBus(1)
    ultraonic_sonic = serial_ultrasonic.ultrasonicSensor(bus)

while True:
        distances = ultraonic_sonic.get_lfr_distances()
        print(f"front: {distances[1]}")
        print(f"left: {distances[0]}")
        print(f"right: {distances[2]}")