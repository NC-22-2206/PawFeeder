#include <virtuabotixRTC.h> // Include the Virtuabotix RTC library
#include <AFMotor.h>       // Include the Adafruit Motor Shield library
#include <Servo.h>         // Include the Servo library

// --- RTC Setup ---
// Connect your DS1302 RTC module as follows:
// DS1302 RST (CE) pin to Arduino Digital Pin 2
// DS1302 DAT (IO) pin to Arduino Digital Pin 3
// DS1302 CLK (SCLK) pin to Arduino Digital Pin 6
virtuabotixRTC myRTC(2, 3, 6); // RST, DAT, CLK pins - UPDATED FOR YOUR PINS

// --- DC Motor Setup ---
// Create a motor object for M1. If your motor is on a different port, change M1 to M2, M3, or M4.
// Using MOTOR12_8BIT is standard and recommended for most DC motors.
AF_DCMotor motor(1);

// --- Servo Motor Setup ---
Servo myServo; // Create a servo object

// --- Constants ---
const int SERVO_PIN = 10; // Digital pin for the servo. If using the shield, D9 or D10 are common.

void setup() {
  Serial.begin(9600); // Initialize serial communication for debugging
  Serial.println("Motor, Servo, & RTC Test Starting...");

  // --- RTC Initialization ---
  // UNCOMMENT THE FOLLOWING LINE *ONLY ONCE* TO SET THE TIME:
  // After setting the time, re-comment it out and re-upload to maintain accuracy.
  // myRTC.setDS1302Time(0, 5, 23, 4, 21, 5, 2025); // Sec, Min, Hour, Day of Week, Day of Month, Month, Year
                                                 // Example: 23:05:00, Thursday, May 21, 2025
                                                 // ADJUST THESE VALUES TO YOUR CURRENT TIME WHEN UNCOMMENTING!
                                                 // Day of Week: 1=Sunday, 2=Monday, ..., 5=Thursday for May 21, 2025

  // --- DC Motor Initialization ---
  motor.setSpeed(0);    // Ensure motor is stopped initially
  motor.run(RELEASE);   // Ensure motor is released/stopped

  // --- Servo Motor Initialization ---
  myServo.attach(SERVO_PIN); // Attaches the servo object to the specified pin
  myServo.write(90);         // Set servo to a starting middle position (90 degrees)
  delay(1000);               // Give the servo time to move to initial position
}

void loop() {
  // --- Read and Print RTC Data ---
  myRTC.updateTime(); // Update the RTC object with current time data
  Serial.print("Current Time: ");
  Serial.print(myRTC.hours);
  Serial.print(":");
  if (myRTC.minutes < 10) Serial.print("0"); // Add leading zero for minutes if less than 10
  Serial.print(myRTC.minutes);
  Serial.print(":");
  if (myRTC.seconds < 10) Serial.print("0"); // Add leading zero for seconds if less than 10
  Serial.print(myRTC.seconds);
  Serial.print(" ");
  Serial.print(myRTC.dayofmonth);
  Serial.print("/");
  Serial.print(myRTC.month);
  Serial.print("/");
  Serial.print(myRTC.year);
  Serial.println();

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
  delay(1200);         // Run for 3 seconds

  Serial.println("DC Motor: Stop");
  motor.run(RELEASE); // Stop the motor
  delay(1000);        // Wait for 1 second

  Serial.println("DC Motor: Backward (Full Speed 255)");
  motor.setSpeed(255); // Set motor speed to full (255)
  motor.run(BACKWARD); // Run motor backward
  delay(1200);         // Run for 3 seconds

  Serial.println("DC Motor: Stop");
  motor.run(RELEASE); // Stop the motor
  delay(2000);        // Wait for 2 seconds before repeating

  // Loop will repeat these actions
  Serial.println("\n--- Cycle Complete, Repeating ---\n");
  delay(3000); // Pause before repeating the entire cycle
}