#include <AFMotor.h>
#include <Servo.h>
#include <virtuabotixRTC.h>

// Function declarations
void dispenseFood();
void parseSchedule(String timesStr);

#define SERVO_PIN 9

Servo foodServo;
virtuabotixRTC myRTC(2, 3, 6);   // CLK, DAT, RST

String scheduleTimes[10];       // Store up to 10 feeding times
int scheduleCount = 0;
String lastActivatedTime = "";   // Track last activated time to prevent re-triggering
bool automaticMode = false;     //<-- ADDED MODE VARIABLE

int restPosition = 0;
int feedPosition = 150;

AF_DCMotor motor1(1); // Changed to motor 1 with appropriate frequency

void setup() {
  delay(2000);  // Give time for motor shield to initialize  motor1.setSpeed(0);  // Start with zero speed
  motor1.run(RELEASE); // Initialize motor state

  Serial.begin(9600);

  pinMode(SERVO_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);

  myRTC.updateTime();
  delay(1000);

  foodServo.attach(SERVO_PIN);
  foodServo.write(restPosition);

  // OPTIONAL: Set RTC time ONCE, then comment out!
  //myRTC.setDS1302Time(0, 44, 12, 7, 22, 5, 2025);   // sec, min, hour, DOW, day, month, year

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
      automaticMode = true;
      Serial.println("[MODE] Automatic mode enabled.");
    } else if (incoming == "GETTIME") {
      Serial.println(currentTimeStr);
    } else if (incoming == "D" || incoming == "FEED") {
      Serial.println("[MANUAL] Dispensing food now...");
      dispenseFood();
      automaticMode = false;
      lastActivatedTime = "";
      Serial.println("[MODE] Automatic mode disabled.");
    } else if (incoming == "AUTO") {
      automaticMode = true;
      Serial.println("[MODE] Automatic mode enabled.");
    } else if (incoming == "MANUAL") {
      automaticMode = false;
      Serial.println("[MODE] Manual mode disabled.");
      lastActivatedTime = "";
    } else if (incoming == "M1F") {
      motor1.run(FORWARD);
      motor1.setSpeed(150);
      Serial.println("[MOTOR] Motor 1 forward.");
    } else if (incoming == "M1B") {
      motor1.run(BACKWARD);
      motor1.setSpeed(150);
      Serial.println("[MOTOR] Motor 1 backward.");
    } else if (incoming == "M1S") {
      motor1.run(RELEASE);
      Serial.println("[MOTOR] Motor 1 stopped.");
    }
  }

  delay(1000); // 1-second loop
}
void dispenseFood() {
  Serial.println("[ACTION] Moving servo to feed position...");
  foodServo.write(feedPosition);
  delay(3000);

  // Quick left wiggle
  foodServo.write(feedPosition - 50);
  delay(250);

  // Quick right wiggle
  foodServo.write(feedPosition + 50);
  delay(250);
  foodServo.write(restPosition);
  Serial.println("[ACTION] Servo movement complete.");
  delay(2000);  // Wait 2 seconds after servo movement
  // Run DC motor forward first  
  Serial.println("[MOTOR 1] Moving FORWARD");
  motor1.run(FORWARD);
  motor1.setSpeed(130);  // Full speed
  delay(500);  // Run longer

  Serial.println("[MOTOR 1] STOP");
  motor1.setSpeed(0);
  motor1.run(RELEASE);
  delay(3000);

  // Then backward  Serial.println("[MOTOR 1] Moving BACKWARD");
  motor1.run(BACKWARD);
  motor1.setSpeed(130);
  delay(500);  // Run longer

  Serial.println("[MOTOR 3] STOP");
  motor1.setSpeed(0);
  motor1.run(RELEASE);

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