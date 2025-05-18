#include <AFMotor.h>

// Initialize motor on M3
AF_DCMotor motor3(3);  // Motor 3 (M3)
AF_DCMotor motor4(4);  // Motor 4 (M3)


void setup() {
  motor3.setSpeed(255);      // Max speed
  motor3.run(FORWARD);       // Spin forward
    motor4.setSpeed(255);      // Max speed
  motor4.run(FORWARD);       // Spin forward
}

void loop() {
  // Nothing here — motor runs continuously
}
