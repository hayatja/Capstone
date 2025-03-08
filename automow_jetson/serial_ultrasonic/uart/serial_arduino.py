from time import sleep
import serial
import sys

# change recursion limit to bypass read failures
sys.setrecursionlimit(30000)

class Arduino():
    """
    Ardiuno object to handle ultrasonic UART data transfer
    """
    def __init__(self):
        try:
            self.serial_port = serial.Serial(
                port="/dev/ttyTHS1",
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1,
            )
            sleep(1)
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

        except Exception as exception_error:
            print("Error starting serial connection. Exiting Program")
            print("Error: " + str(exception_error))
            self.serial_port.close()

    def read(self):
        """
        waits until buffer recieves data then read UART buffer
        """
        try:
                
            data_rcvd = self.serial_port.read(size = self.serial_port.in_waiting)
            # maybe return code if you later find it useful
            return data_rcvd
        except Exception as exception_error:
            print("Error reading serial connection. Exiting Program")
            print("Error: " + str(exception_error))
            self.serial_port.close()

    def write(self, data):
        """
        write data to UART
        """
        try:    
            code = self.serial_port.write(data)
            return code
        except Exception as exception_error:
            print("Error writing serial connection. Exiting Program")
            print("Error: " + str(exception_error))
            self.serial_port.close()

    def serial_close(self):
        self.serial_port.close()


    def get_ultrasonic_distance(self):
        """
        Send arduino command to measure distance then wait and recieve distance data from Arduino 
        """
        try:
            code = self.write("1".encode())
            distance = str(self.read())
            
            # parse distance hex to decimal
            distance = distance[distance.index("x"):distance.index("x")+3]
            distance = '0' + distance
            distance = int(distance, 0)
        except:
            distance = self.get_ultrasonic_distance()
        
        return distance