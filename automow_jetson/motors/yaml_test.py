import yaml

class motor_pins():
    def __init__(self):
        with open('motor_pin_definitions.yaml', 'r') as file:
            self.MOTOR_PINS = yaml.safe_load(file)

    def print(self):
        print(self.MOTOR_PINS)
            
p = motor_pins()
p.print()