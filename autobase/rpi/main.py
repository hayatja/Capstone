from adc.ads import ADS1115
from temperature.mpu6050 import TemperatureSensor
from smbus2 import SMBus    #import SMBus module of I2C
from time import sleep
import requests

SERVER_URL = "http://192.168.74.197:8000"

if __name__ == "__main__":
    # http client session
    session = requests.sessions.Session()

    # initialize devices
    bus = SMBus(1)

    # adc for soil moisture and rain level sensor
    adc = ADS1115() 
    # integrated MPU6050 temperature sensor
    temperature_sensor = TemperatureSensor(bus) 

    while True:
        adc.configure_soil_moisture_read(bus)
        sleep(0.5) # delay is needed after configuration register reconfigurations
        soil_moisture = adc.read_adc(bus)
        print("soil moisture: " + str(soil_moisture))


        adc.configure_rain_level_read(bus)
        sleep(0.5) # delay is needed after configuration register reconfigurations
        rain_level = adc.read_adc(bus)
        print("soil rain level: " + str(rain_level))

        temperature = temperature_sensor.read_temperature(bus)
        print("temperature is: " + str(temperature))

        payload = {"temperature": temperature, 
                   "soil_moisture": soil_moisture, 
                   "rain_level": rain_level}
        
        # send data in http post to the server
        try:
            response = session.post(SERVER_URL, json = payload, timeout = 2)
            
            if response.status_code == 200:
                print("Dictionary sent successfully!")
            else:
                print(f"Failed to send dictionary. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
        
        sleep(20)