from yaml import safe_load
import RPi.GPIO as jio

class PowerController():
    # limits power to motor logic circuits
    def __init__(self):
        with open('motors/motor_pin_definitions.yaml', 'r') as file:
            CONFIG = safe_load(file)
        self.pin = CONFIG.get("POWER_CONTROL_PIN")
    
    def power_on(self):
        jio.output(self.pin, jio.HIGH)
        pass
    
    def power_off(self):    
        jio.output(self.pin, jio.LOW)
        pass
