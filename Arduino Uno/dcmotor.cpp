#include <AFMotor.h>
#include <Servo.h>
#include <virtuabotixRTC.h>

#define SERVO_PIN 11

Servo foodServo;
virtuabotixRTC myRTC(2, 3, 6);   // CLK, DAT, RST

String scheduleTimes[10];       // Store up to 10 feeding times
int scheduleCount = 0;
String lastActivatedTime = "";   // Track last activated time to prevent re-triggering
bool automaticMode = false;     //<-- ADDED MODE VARIABLE

int restPosition = 0;
int feedPosition = 150;

AF_DCMotor motor3(3); // assign motor 3

void setup() {
  motor3.setSpeed(255);      // set default speed for motor3
  motor3.run(RELEASE);         // set motor3 to off

  Serial.begin(9600);

  pinMode(SERVO_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);

  myRTC.updateTime();
  delay(1000);

  foodServo.attach(SERVO_PIN);
  foodServo.write(restPosition);

  // OPTIONAL: Set RTC time ONCE, then comment out!
  //myRTC.setDS1302Time(0, 19, 15, 7, 18, 5, 2025);   // sec, min, hour, DOW, day, month, year

  Serial.println("[SYSTEM] Dog Feeder Initialized.");
}

void loop() {
  myRTC.updateTime();

  int hour = myRTC.hours;
  int minute = myRTC.minutes;
  int second = myRTC.seconds;

  if (hour < 0 || hour > 23 || minute > 59 || second > 59) {
    Serial.println("[ERROR] Invalid RTC time detected.");
    return;
  }

  char currentTime[9];
  sprintf(currentTime, "%02d:%02d:%02d", hour, minute, second);
  String currentTimeStr = String(currentTime);

  Serial.print("[RTC] Time: ");
  Serial.println(currentTimeStr);

  if (automaticMode) {   // Only check schedule if in automatic mode
    for (int i = 0; i < scheduleCount; i++) {
      if (scheduleTimes[i] == currentTimeStr && lastActivatedTime != currentTimeStr) {
        Serial.println("[MATCH] Feeding time matched!");
        dispenseFood();
        lastActivatedTime = currentTimeStr;
        break; // Exit the loop after finding a match
      }
    }
  }

  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    Serial.print("[SERIAL INPUT] ");
    Serial.println(incoming);

    if (incoming.startsWith("SCHEDULE:")) {
      String timesStr = incoming.substring(9);
      parseSchedule(timesStr);
      automaticMode = true; // Enable automatic mode when schedule is received
      Serial.println("[MODE] Automatic mode enabled.");
    } else if (incoming == "GETTIME") {
      Serial.println(currentTimeStr);
    } else if (incoming == "D" || incoming == "FEED") {
      Serial.println("[MANUAL] Dispensing food now...");
      dispenseFood();
      automaticMode = false; // Disable automatic mode for manual dispense
      lastActivatedTime = "";   //reset
      Serial.println("[MODE] Automatic mode disabled.");
    } else if (incoming == "AUTO") { //<-- Added AUTO command
        automaticMode = true;
        Serial.println("[MODE] Automatic mode enabled.");
    } else if (incoming == "MANUAL") { //<-- Added MANUAL command
        automaticMode = false;
        Serial.println("[MODE] Manual mode disabled.");
        lastActivatedTime = ""; //reset lastActivatedTime
    } else {
      // Manual motor control (for testing or other purposes)
      if (incoming == "M3F") {
        motor3.run(FORWARD);
        motor3.setSpeed(255);
        Serial.println("[MOTOR] Motor 3 forward.");
      } else if (incoming == "M3B") {
        motor3.run(BACKWARD);
        motor3.setSpeed(255);
        Serial.println("[MOTOR] Motor 3 backward.");
      } else if (incoming == "M3S") {
        motor3.run(RELEASE);
        Serial.println("[MOTOR] Motor 3 stopped.");
      }
    }
  }

  delay(1000); // 1-second loop
}
void dispenseFood() {
  Serial.println("[ACTION] Moving servo to feed position...");
  foodServo.write(feedPosition);
  delay(3000); // Stay at feed position for a short duration

  // Quick left wiggle
  foodServo.write(feedPosition - 50); // Move 10 degrees to the left
  delay(250); // Shorter delay for a quick wiggle

  // Quick right wiggle
  foodServo.write(feedPosition + 50); // Move 10 degrees to the right
  delay(250); // Shorter delay for a quick wiggle

  foodServo.write(restPosition);
  Serial.println("[ACTION] Servo movement complete.");

  delay(2000); // Wait for 2 seconds before moving the motor

  // *** DC Motor Control Sequence ***
  Serial.println("[MOTOR 3] Moving BACKWARD");
  motor3.run(BACKWARD);
  delay(1200);

  Serial.println("[MOTOR 3] STOP");
  motor3.run(RELEASE);
  delay(10000);

  Serial.println("[MOTOR 3] Moving FORWARD");
  motor3.run(FORWARD);
  delay(1200);

  Serial.println("[MOTOR 3] STOP");
  motor3.run(RELEASE);
  delay(5000);

  Serial.println("[ACTION] Food dispensed.");
}

void parseSchedule(String timesStr) {
  scheduleCount = 0;
  int start = 0;

  while (start < timesStr.length()) {
    int commaIndex = timesStr.indexOf(',', start);
    if (commaIndex == -1) commaIndex = timesStr.length();

    String t = timesStr.substring(start, commaIndex);
    t.trim();

    if (t.length() == 8 && t.indexOf(':') == 2 && t.lastIndexOf(':') == 5) {
      scheduleTimes[scheduleCount++] = t;
      Serial.print("[DEBUG] Time added: ");
      Serial.println(t);
    } else {
      Serial.print("[ERROR] Invalid time format: ");
      Serial.println(t);
    }

    start = commaIndex + 1;
    if (scheduleCount >= 10) break;
  }
}