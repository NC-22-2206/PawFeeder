#include <AFMotor.h>

#include <Servo.h>
#include <virtuabotixRTC.h>


#define SERVO_PIN 10

Servo foodServo;
virtuabotixRTC myRTC(2, 3, 4);  // CLK, DAT, RST

String scheduleTimes[10];       // Store up to 10 feeding times
int scheduleCo      unt = 0;
String lastActivatedTime = "";  // Track last activated time to prevent re-triggering

int restPosition = 0;
int feedPosition = 90;

AF_DCMotor motor3(3); // assign 

void setup() {
  motor3.setSpeed(200); // set default speed
  motor3.run(RELEASE); // set motor to off

  Serial.begin(9600);

  pinMode(SERVO_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);

  myRTC.updateTime();
  delay(1000);

  foodServo.attach(SERVO_PIN);
  foodServo.write(restPosition);

  // OPTIONAL: Set RTC time ONCE, then comment out!
  // myRTC.setDS1302Time(0, 13, 13, 7, 23, 3, 2025);  // sec, min, hour, DOW, day, month, year

  Serial.println("[SYSTEM] Dog Feeder Initialized.");
  
}

void loop() {


  // This code depends whether it's automatic or manual. Manual for button inputs such as below. Automatic adds a loop to the whole algorithm for automatic dispensing.
  // start
  motor3.run(FORWARD); // motor runs forwards (changes depending on the DC Motor orientation)

  motor3.setSpeed(200); // set speed for the rotation
  delay(10); // delay before turning off (can change depending on how far the platform extends)
  motor3.run(RELEASE) // turn off DC motor 
  delay(10) // delay before retracting personal preference

  motor3.run(BACKWARD) // motor runs opposite to retract
  motor3.setSpeed(200)
  delay(10); // delay before retracting to previous position (the platform goes back in for refill or whatever)
  motor3.run(RELEASE) // turn off DC motor for another input
  //end of code.

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

  for (int i = 0; i < scheduleCount; i++) {
    if (scheduleTimes[i] == currentTimeStr && lastActivatedTime != currentTimeStr) {
      Serial.println("[MATCH] Feeding time matched!");
      dispenseFood();
      lastActivatedTime = currentTimeStr;
      break;
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
    } else if (incoming == "GETTIME") {
      Serial.println(currentTimeStr);
    } else if (incoming == "D" || incoming == "FEED") {
      Serial.println("[MANUAL] Dispensing food now...");
      dispenseFood();
    }
  }

  delay(1000); // 1-second loop

}

void dispenseFood() {
  Serial.println("[ACTION] Moving servo to feed position...");
  foodServo.write(feedPosition);
  delay(5000); // Stay open for 5 seconds
  foodServo.write(restPosition);
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
