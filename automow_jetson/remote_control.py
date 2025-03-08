# script may be executed to remotely control the AutoMow using a keyboard

import sys
import tty
import termios
from motors import pwm
import RPi.GPIO as jio
import traceback

def get_keyboard_input():
    # get one press from standard input
    print("Press any key: ", end='', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

class Controller():
    """
    remote control class for the automow
    """
    def run():
        body = pwm.Body()
        # Call the function
        while True:
            # get user input
            command = get_keyboard_input()
            
            # interpret command
            if command == "l":
                exit()
            
            elif command == "w":
                body.move_forward()
                print("moving forward")
            
            elif command == "1":
                body.step_forward()
                print("stepping forward")
            
            elif command == "s":
                body.move_backward()
                print("moving backward")
            
            elif command == " ":
                body.stop()
            
            elif command == "d":
                body.spin_cw()            
            
            elif command == "a":
                body.spin_ccw()
            
            elif command == "e":
                body.spin_cw(spin_time=None)            
            
            elif command == "q":
                body.spin_ccw(spin_time=None)

            elif command == "p":
                body.slide_right()

            elif command == "o":
                body.slide_left()
            
            elif command == "u":
                body.change_speed(body.right_side.current_frequency + 100)

            elif command == "j":
                body.change_speed(body.right_side.current_frequency - 100)
            
            elif command == ";":
                # left side
                body.sides[0].pwm.ChangeFrequency(body.sides[0].pwm._frequency_hz + 15)

            elif command == ".":
                # left side
                body.sides[0].pwm.ChangeFrequency(body.sides[0].pwm._frequency_hz - 15)

            elif command == "'":
                # right side
                body.sides[1].pwm.ChangeFrequency(body.sides[1].pwm._frequency_hz + 15)

            elif command == "/":
                # right side
                body.sides[1].pwm.ChangeFrequency(body.sides[1].pwm._frequency_hz - 15)

            elif command == "m":
                # Toggle mower motor
                if body.mower_motor.state:
                    body.tunr_off_mower()
                else:
                    body.tunr_on_mower()
            
            else:
                print(f"{command} is not a valid input")

if __name__ == "__main":
    try:
        Controller.run()

    except Exception as e:
        print(traceback.format_exc())

    finally:
        jio.cleanup()
                  
