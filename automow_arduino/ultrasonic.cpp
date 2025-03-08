#include <Arduino.h>
# include "ultrasonic.h"

/* HC-SR04 ultrasonic sensor has four pins
Vcc: 5V power voltage
Ground: Ground refernce
Trig: output pin, will trigger ultrasonic sensing
Echo: to be configured as input, recieves bounced ultrasonic waves
*/

// Constructor for 4 pin ultrasonic sensor
UltrasonicSensor4Pin::UltrasonicSensor4Pin(int trigPin, int echoPin) {
    this->trigPin = trigPin;
    this->echoPin = echoPin;
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
}
// Function to get distance in centimeters
int UltrasonicSensor4Pin::getDistanceCM() {
  // Trigger pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Measure echo pulse duration
  long duration = pulseIn(echoPin, HIGH);

  // Calculate distance in centimeters
  int distanceCM = duration * 0.034 / 2;
  return distanceCM;
}


/* The Parallax PING ultrasonic sensor has three pins
Vcc: 5V power voltage
Ground: Ground refernce
Ping: combined ping and echo pin
*/ 

// Constructor for 3 pin ultrasonic sensor
UltrasonicSensor3Pin::UltrasonicSensor3Pin(int pingPin) {
    this->pingPin = pingPin;
}

// Function to get distance in centimeters
int UltrasonicSensor3Pin::getDistanceCM() {
    // The PING))) is triggered by a HIGH pulse of 2 or more microseconds.
    // Give a short LOW pulse beforehand to ensure a clean HIGH pulse:
    pinMode(pingPin, OUTPUT);
    digitalWrite(pingPin, LOW);
    delayMicroseconds(2);
    digitalWrite(pingPin, HIGH);
    delayMicroseconds(5);
    digitalWrite(pingPin, LOW);

    // The same pin is used to read the signal from the PING a HIGH pulse 
    // (in microseconds) from the sending of the ping whose duration
    // is the time to the reception of its echo off of an object.
    pinMode(pingPin, INPUT);
    long duration = pulseIn(pingPin, HIGH);
    
    // The speed of sound is 340 m/s or 29 microseconds per centimeter.
    // The ping travels out and back, so to find the distance of
    // the object we take half of the distance travelled.
    int cm = duration / 29 / 2;
    return cm;
}


