#include <AFMotor.h> // Include the Adafruit Motor Shield library
#include <Servo.h>   // Include the Servo library

// --- DC Motor Setup ---
// Create a motor object for M1. If your motor is on a different port, change M1 to M2, M3, or M4.
AF_DCMotor motor(1, MOTOR12_8KHZ); // M1 on the shield, 8KHz speed control

// --- Servo Motor Setup ---
Servo myServo; // Create a servo object

// --- Constants ---
const int SERVO_PIN = 9; // Digital pin for the servo. If using the shield, D9 or D10 are common.
                         // If not using the shield's servo pins, choose any PWM-capable pin (3, 5, 6, 9, 10, 11 on Uno).

void setup() {
  Serial.begin(9600); // Initialize serial communication for debugging
  Serial.println("Motor & Servo Test Starting...");

  // --- DC Motor Initialization ---
  motor.setSpeed(0);   // Ensure motor is stopped initially
  motor.run(RELEASE); // Ensure motor is released/stopped

  // --- Servo Motor Initialization ---
  myServo.attach(SERVO_PIN); // Attaches the servo object to the specified pin
  myServo.write(90);         // Set servo to a starting middle position (90 degrees)
  delay(1000);               // Give the servo time to move to initial position
}

void loop() {
  // --- Servo Motor Test (First) ---
  Serial.println("Servo Motor: Moving to 90 degrees");
  myServo.write(90); // Move servo to 90 degrees
  delay(1000);       // Wait for 1 second

  Serial.println("Servo Motor: Moving to 0 degrees");
  myServo.write(0); // Move servo to 0 degrees
  delay(1000);      // Wait for 1 second

  Serial.println("Servo Motor: Moving to 90 degrees");
  myServo.write(90); // Move servo to 90 degrees
  delay(1000);       // Wait for 1 second

  Serial.println("Servo Motor: Moving to 0 degrees");
  myServo.write(0); // Move servo to 0 degrees
  delay(1000);      // Wait for 1 second

  Serial.println("Servo Motor: Returning to 90 degrees (resting position)");
  myServo.write(90); // Return servo to 90 degrees
  delay(1500);       // Wait a bit before DC motor starts

  // --- DC Motor Test (Next) ---
  Serial.println("DC Motor: Forward (Full Speed 255)");
  motor.setSpeed(255); // Set motor speed to full (255)
  motor.run(FORWARD);  // Run motor forward
  delay(3000);         // Run for 3 seconds

  Serial.println("DC Motor: Stop");
  motor.run(RELEASE); // Stop the motor
  delay(1000);        // Wait for 1 second

  Serial.println("DC Motor: Backward (Full Speed 255)");
  motor.setSpeed(255); // Set motor speed to full (255)
  motor.run(BACKWARD); // Run motor backward
  delay(3000);         // Run for 3 seconds

  Serial.println("DC Motor: Stop");
  motor.run(RELEASE); // Stop the motor
  delay(2000);        // Wait for 2 seconds before repeating

  // Loop will repeat these actions
  Serial.println("\n--- Cycle Complete, Repeating ---\n");
  delay(3000); // Pause before repeating the entire cycle
}