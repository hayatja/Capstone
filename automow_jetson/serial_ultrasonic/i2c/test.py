import smbus
import serial_ultrasonic
from time import sleep

# Create an smbus object (you might need to change the bus number)
bus = smbus.SMBus(1)

while True:
    ultraonic_sonic = serial_ultrasonic.ultrasonicSensor(bus)
    distances = ultraonic_sonic.get_lfr_distances()
    print(f"front: {distances[1]}")
    print(f"left: {distances[0]}")
    print(f"right: {distances[2]}")