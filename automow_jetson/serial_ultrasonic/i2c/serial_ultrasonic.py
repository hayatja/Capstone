# class to communicate with ultrasonic sensor on an arduino through I2C

# I2C address of the Arduino peripheral
ARDUINO_ADDRESS = 11

class ultrasonicSensor():
    """
    Abstraction layer for the ultrasonic sensor
        distance is pulled from the arduino through i2c
    """
    def __init__(self, bus):
        self.bus = bus
    
    def get_lfr_distances(self):
        """
        returns distances from three directions through ultrasonic sensor
        takes about 20ms to execute 
        reurns:
            tuple of distances to the closest obstacle (left, front, right)
        """
        data = self.bus.read_i2c_block_data(ARDUINO_ADDRESS, 0, 3)
        
        distance_left = data[0]
        distance_front = data[1]
        distance_right = data[2]

        distances = (distance_left, distance_front, distance_right)
        return distances

