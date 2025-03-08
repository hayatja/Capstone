import RPi.GPIO as jio

# Mower pin state deffinitions 
OFF_STATE = 0
ON_STATE = 1

class MowerMotor():
    """
    Blade motor control class
    """
    def __init__(self, pin_number):
        self.pin_number = pin_number
        jio.setup(self.pin_number, jio.OUT, initial = OFF_STATE)
        self.state = False

    def turn_on(self):
        jio.output(self.pin_number, ON_STATE)
        self.state = True

    def turn_off(self):
        jio.output(self.pin_number, OFF_STATE)
        self.state = False
        