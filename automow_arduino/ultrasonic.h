#ifndef ULTRASONIC_H
#define ULTRASONIC_H

/* HC-SR04 ultrasonic sensor has four pins
Vcc: 5V power voltage
Ground: Ground refernce
Trig: output pin, will trigger ultrasonic sensing
Echo: to be configured as input, recieves bounced ultrasonic waves
*/ 
class UltrasonicSensor4Pin {
private:
    int trigPin;
    int echoPin;

public:
    // Constructor for 4 pin ultrasonic sensor
    UltrasonicSensor4Pin(int trigPin, int echoPin);
    // Function to get distance in centimeters
    int getDistanceCM();
};

/* The Parallax PING ultrasonic sensor has three pins
Vcc: 5V power voltage
Ground: Ground refernce
Ping: combined ping and echo pin
*/ 
class UltrasonicSensor3Pin {
private:
    int pingPin;
public:
    // Constructor
    UltrasonicSensor3Pin(int pingPin);

    // Function to get distance in centimeters
    int getDistanceCM();
};

#endif
