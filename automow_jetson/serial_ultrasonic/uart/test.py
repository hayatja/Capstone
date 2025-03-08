import serial_arduino
from time import sleep
import traceback

sonic_sensor = serial_arduino.Arduino()

try:
    while True:
        distance = sonic_sensor.get_ultrasonic_distance()
        print(f"distance: {distance}")
except Exception as e:
    print(traceback.format_exc())