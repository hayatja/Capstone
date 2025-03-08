"""
Test API
"""
# initiate i2c bus object for ultrasonic
import smbus
bus = smbus.SMBus(1)

# import and initiate ultrasonic sensor
from serial_ultrasonic.i2c import serial_ultrasonic
ultrasonic = serial_ultrasonic.ultrasonicSensor(bus)

from threading import Thread
from time import sleep
from flask import Flask, request, jsonify
from typing import Optional, List, Tuple
# import cv2

# from motors import pwm
from motors.pwm import Body
body = Body()

# from color_detection import detect_border
from pathfinding.pathing import Mowing, Observer, Landscape, Point, UltrasonicSensor, D, Mapping

app = Flask(__name__)
# videoCaptureObject = cv2.VideoCapture(1)

is_running: bool = False
mow_ongoing: bool = False
going_to_base: bool = False
sensor_land: Optional[List[List[int]]] = None
observer: Optional[Observer] = None
mock_map: Optional[List[List[int]]] = None


def reset_mowing_params() -> None:
    global sensor_land, observer, mock_map

    sensor_land = Landscape.generate_empty_land(6, 4)

    observer = Observer(
        position=Point(0, 0),
        height=1,
        width=1,
        direction=D.S,
        left_sensor=UltrasonicSensor(),
        front_sensor=UltrasonicSensor(),
        right_sensor=UltrasonicSensor()
    )

    mock_map = Mapping.generate_mock_map(6, 4)


def go_to_base() -> None:
    global going_to_base, observer, sensor_land

    if going_to_base:
        required_steps = Mowing.back_to_start(
            pos=(observer.position.y, observer.position.x),
            matrix=sensor_land,
            direction=observer.direction
        )

        for step in required_steps:
            # assign motor moves
            if step == "forward":
                body.step_forward()
            
            elif step == "left":
                body.spin_ccw()
            
            elif step == "right":
                body.spin_cw()

            print(step)
            sleep(1)

    going_to_base = False


def get_aggregate_ultrasonic_data() -> Tuple[int, int, int]:
    global observer

    sample_size = 5  # change this for more accuracy but slower results
    raw_data = []

    for i in range(sample_size):
        # TODO: update this when real sensors working# TODO: update this when real sensors working
        sleep(0.1)
        read_data = ultrasonic.get_lfr_distances()
        # read_data = Mapping.get_mock_scan_reads(
        #     m=mock_map,
        #     p=(observer.position.y, observer.position.x),
        #     d=observer.direction
        # )
        raw_data.append(read_data)

    print(raw_data)

    aggregate_data = [-1, -1, -1]

    for i in range(3):
        values_at_index = [t[i] for t in raw_data]
        median_value = sorted(values_at_index)[len(values_at_index) // 2]
        aggregate_data[i] = median_value

    return aggregate_data[0], aggregate_data[1], aggregate_data[2]


def move_mower() -> None:
    global is_running, mow_ongoing, body

    temp_index = 2000
    while True:
        body.tunr_on_mower()

        if is_running:
            temp_index -= 1

            sensor_mowing_step = Mowing.calculate_next_step(
                current_map=sensor_land,
                observer=observer,
                sensor_data=get_aggregate_ultrasonic_data()
            )

            if sensor_mowing_step == "stop":
                is_running = False
                break

            # ----------

            backing_test = Mowing.back_to_start(
                pos=(observer.position.y, observer.position.x),
                matrix=sensor_land,
                direction=observer.direction
            )
            print(f"To go back from {(observer.position.y, observer.position.x)}: {backing_test}")

            print(Landscape.land_str(sensor_land))
            print("  " + "".join(str(i)[-1] for i in range(len(sensor_land[0]))))
            print("-------------------")

            # ----------

            print(sensor_mowing_step, observer.direction)
            print("=====")

            if sensor_mowing_step == "forward":
                body.step_forward()
            
            elif sensor_mowing_step == "left":
                body.spin_ccw()
            
            elif sensor_mowing_step == "right":
                body.spin_cw()

        else:
            break

        sleep(1)

    mow_ongoing = False
    reset_mowing_params()


@app.route("/detect-color", methods=["POST"])
def detect_color():
    # TODO: revert for color detection

    # global videoCaptureObject
    # detected = detect_border.check(videoCaptureObject)

    return jsonify({"message": "Success", "detected": True})


@app.route("/set-state", methods=["POST"])
def move_api():
    """
    Rest API for movement of the AutoMow

    Allowed states:
    - Running
    - Stopped
    - Paused
    """

    global is_running, mow_ongoing, going_to_base, sensor_land, observer, mock_map

    try:
        # Assuming the request data is in JSON format
        data = request.get_json()
        state = data["switch_state"]

        print(state)

        if state == "RUNNING":
            if going_to_base:
                return jsonify({"message": "Failure", "cause": "AutoMow is returning to base"})

            print("Running AutoMow...")
            is_running = True

            if not mow_ongoing:
                Thread(target=move_mower, name='mowing_thread').start()

            mow_ongoing = True

        elif state == "STOPPED":
            print("Stopping AutoMow...")
            is_running = False
            mow_ongoing = False

            # TODO: comment next two lines to disable back to base
            going_to_base = True
            Thread(target=go_to_base, name='backing_thread').start()

            reset_mowing_params()

        elif state == "PAUSED":
            if going_to_base:
                return jsonify({"message": "Failure", "cause": "AutoMow is returning to base"})

            print("Pausing AutoMow...")
            is_running = False

        else:
            failed_message = {"message": "Failure", "cause": "invalid requested state"}
            return jsonify(failed_message)

        result = {"message": "Success", "new_state": state}

        # Return the result as JSON
        return jsonify(result)

    except Exception as e:
        # Handle errors
        error_message = {"error": str(e)}
        return jsonify(error_message), 500


if __name__ == "__main__":
    try:
        reset_mowing_params()
        app.run(port=5002, debug=True)
    finally:
        body.tunr_off_mower()
        body.clean_up()
