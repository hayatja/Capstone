/*
Arduino loop is constantly scanning for distance to the
closest obstacle in three directions (left, front, right)
Upon I2C request, The Arduino will return three uint8_t, 
one for each direction in this order:
  1- distance left
  2- distance front
  3- distance right
*/

# include "stdlib.h"
# include <Wire.h>
# include "ultrasonic.h"

// Define ardiuno I2C address
#define I2C_ADDRESS 11

// front sensor pins
const int trigPin_1 = 2;
const int echoPin_1 = 4;
// left and right sensors pins
const int pingPin_R = 12;
const int pingPin_L = 5;

// varriable to store latest ultrasonic distance
uint8_t distance_front = 0;
uint8_t distance_left = 0;
uint8_t distance_right = 0;

// Function to handle I2C data requests
void requestEvent() {
  uint8_t payload [] = {distance_left, distance_front, distance_right};
  for (uint8_t i = 0; i < sizeof(payload); i++) {
    Wire.write(payload[i]);
  }
}

// ultrasonic constructors initiation
// differnet classes because different sensors were used 
UltrasonicSensor4Pin ultrasonic_sensor_front(trigPin_1, echoPin_1);
UltrasonicSensor3Pin ultrasonic_sensor_right(pingPin_R);
UltrasonicSensor3Pin ultrasonic_sensor_left(pingPin_L);

void setup() {
  Serial.begin(9600);

  // Initialize I2C communication
  Wire.begin(I2C_ADDRESS);

  // Register the requestEvent function
  Wire.onRequest(requestEvent);
}


void loop() {
  // keep scanning distances, return if jetson requests
  distance_front = ultrasonic_sensor_front.getDistanceCM();
  distance_right = ultrasonic_sensor_right.getDistanceCM();
  distance_left = ultrasonic_sensor_left.getDistanceCM();
}
