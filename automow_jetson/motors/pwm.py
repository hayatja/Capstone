import RPi.GPIO as jio
from time import sleep
from yaml import safe_load
from motors.power_controller import PowerController
from motors import mower_motor

# config file looks like this:
# MOTOR_PINS:
#     RIGHT_SIDE: 
#         PWM_PIN: 
#           PIN_NUMBER: 32
#         DIRECTION_PINS:
#             BACK: 
#               PIN_NUMBER: 37
#             FRONT: 
#               PIN_NUMBER: 35
#     LEFT_SIDE: 
#         PWM_PIN: 
#           PIN_NUMBER: 33
#         DIRECTION_PINS:
#             BACK: 
#               PIN_NUMBER: 36
#             FRONT: 
#               PIN_NUMBER: 38
# POWER_CONTROL_PIN: 11
# MOWER_MOTOR_PIN: 22

BASELINE_FREQUENCY = 350 # frequency to prevent slipping when starting motors or changing directions
MOTOR_FORWARD = 1
MOTOR_BACKWARD = 0

class Motor():
    """
    Stepper motor class
    """
    def __init__(self, direction_pin):
        """
        Args:
            direction_pin (int): gpio pin nubmer responsible for motor
                                 direction multiplexer
        """
        # setup gpio
        jio.setup(direction_pin, jio.OUT, initial = MOTOR_FORWARD)
        self.current_direction_state = MOTOR_FORWARD
        self.direction_pin = direction_pin
    
    def set_foward(self):
        self.current_direction_state = MOTOR_FORWARD
        jio.output(self.direction_pin, self.current_direction_state)
    
    def set_backward(self):
        self.current_direction_state = MOTOR_BACKWARD
        jio.output(self.direction_pin, self.current_direction_state)

class Side():
    """
    One side of the AutoMow, controlling front and back motors
    """
    def __init__(self, pwm_frequency, SIDE_PIN_DICT):
        """
        prarams:
            pwm_frequency (int): initialization pwm frequency
        """
        self.motor_power_controller = PowerController()
        self.motor_power_controller.power_off()

        # extract direction pins dictionary
        DIRECTION_PINS_DICT = SIDE_PIN_DICT.get("DIRECTION_PINS")
        # extract front direction control pins
        self.front_direction_pin = DIRECTION_PINS_DICT.get("FRONT").get("PIN_NUMBER")
        # extract back direction control pins
        self.back_direction_pin = DIRECTION_PINS_DICT.get("BACK").get("PIN_NUMBER")
        
        # initialize back and fron motors for the side
        self.front_motor = Motor(self.front_direction_pin)
        self.back_motor = Motor(self.back_direction_pin)
        self.motors = [self.front_motor, self.back_motor]

        # set pwm speed control pin
        self.pwm_pin = SIDE_PIN_DICT.get("PWM_PIN").get("PIN_NUMBER")
        jio.setup(self.pwm_pin, jio.OUT, initial = jio.LOW)
        self.pwm = jio.PWM(self.pwm_pin, pwm_frequency)
        self.current_frequency = pwm_frequency

    def start_motors(self):
        # start motor movement with duty cycle 50 and with the origianlly set frequency
        self.pwm.start(50)
        self.pwm.ChangeDutyCycle(50)
        self.motor_power_controller.power_on()

    def stop_motors(self):
        # stop motor movement and cut power to motor control circuits
        self.motor_power_controller.power_off()
        self.pwm.ChangeDutyCycle(0)

    def change_frequency(self, frequency):
        # change side speed
        self.pwm.ChangeFrequency(frequency)


class Body():
    """
    Automow body controlling two sides (four motors) at each corner of AutoMow body
    """
    def __init__(self):
        jio.setmode(jio.BOARD)
        with open('motors/motor_pin_definitions.yaml', 'r') as file:
            CONFIG = safe_load(file)
        MOTOR_PINS = CONFIG.get("MOTOR_PINS")

        self.current_frequency = 200
        self.left_side = Side(BASELINE_FREQUENCY, MOTOR_PINS.get("LEFT_SIDE"))
        self.right_side = Side(BASELINE_FREQUENCY, MOTOR_PINS.get("RIGHT_SIDE"))
        self.sides = [self.left_side, self.right_side]
        
        MOWER_MOTOR_PIN = CONFIG.get("MOWER_MOTOR_PIN")
        self.mower_motor = mower_motor.MowerMotor(MOWER_MOTOR_PIN)

    def move(self, stop_time = None):
        # launch motor movement
        for side in self.sides:
            side.start_motors()
        self.change_speed(BASELINE_FREQUENCY)
        
        # stop if a stop_time is provided
        if stop_time:
            sleep(stop_time)
            self.stop()

    def move_forward(self):
        # always start with baseline to prevent slipping
        self.stop()
        sleep(0.2)
        
        # Set all motors for forward operation
        for side in self.sides:
            for motor in side.motors:
                motor.set_foward()
        # start both pwm sides
        self.move()

    def step_forward(self):        
        # Set all motors for forward operation
        for side in self.sides:
            for motor in side.motors:
                motor.set_foward()
        # start both pwm sides one grid step
        self.move(stop_time = 0.45)


    def move_backward(self):
        # reverse motor direction
        for side in self.sides:
            for motor in side.motors:
                motor.set_backward()
        self.move()
    
    def stop(self):
        #stop automow body
        # change speed to slowly stop
        self.change_speed(150)
        # stop both motor sides
        self.left_side.stop_motors()
        self.right_side.stop_motors()
    
    def change_speed(self, targ_frequency, time_interval_between_increments = 0.1, frequency_increment = 25):
        """
        Change automow body speed
        Args
            targ_frequency: target speed frequency
            time_interval_between_increments: sleep time between frequency increments
            frequency_increment: frequency step between sleeps
        """
        # gradually change speed to prevent slipping
        while(self.current_frequency != targ_frequency):
            # decide increment change
            if (self.current_frequency < targ_frequency):
                self.current_frequency = self.current_frequency + frequency_increment
            if (self.current_frequency > targ_frequency):
                self.current_frequency = self.current_frequency - frequency_increment
            # change pwms frequency
            self.left_side.change_frequency(self.current_frequency)
            # self.right_side.change_frequency(self.current_frequency)
            self.right_side.change_frequency(self.current_frequency + 2)
            sleep(time_interval_between_increments)
    
    def spin_cw(self, spin_time = 2.4):
        # operate the wheels to spin automow clockwise
        for motor in self.left_side.motors:
            motor.set_foward()
        for motor in self.right_side.motors:
            motor.set_backward()

        self.right_side.change_frequency(BASELINE_FREQUENCY)
        self.left_side.change_frequency(BASELINE_FREQUENCY)
        # spin 90 degrees
        self.move(spin_time)

    def spin_ccw(self, spin_time = 2.4):
        # operate the wheels to spin automow
        for motor in self.right_side.motors:
            motor.set_foward()
        for motor in self.left_side.motors:
            motor.set_backward()

        self.right_side.change_frequency(BASELINE_FREQUENCY)
        self.left_side.change_frequency(BASELINE_FREQUENCY)
        # spin 90 degrees
        self.move(spin_time)

    def slide_right(self):
        # use butterfly wheel functionality to slide
        self.stop()
        self.left_side.front_motor.set_foward()
        self.left_side.back_motor.set_backward()

        self.right_side.front_motor.set_backward()
        self.right_side.back_motor.set_foward()
        self.move()

    def slide_left(self):
        # use butterfly wheel functionality to slide
        self.stop()
        self.right_side.front_motor.set_foward()
        self.right_side.back_motor.set_backward()

        self.left_side.front_motor.set_backward()
        self.left_side.back_motor.set_foward()
        self.move()
    
    def tunr_on_mower(self):
        # turn on the blade motor
        self.mower_motor.turn_on()

    def tunr_off_mower(self):
        # turn off the blade motor
        self.mower_motor.turn_off()

    def clean_up(self):
        jio.cleanup()
        print("cleaned up")