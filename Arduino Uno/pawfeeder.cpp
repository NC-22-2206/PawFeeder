#include <Servo.h>
#include <virtuabotixRTC.h>


#define SERVO_PIN 10


Servo foodServo;
virtuabotixRTC myRTC(2, 3, 4);  // CLK, DAT, RST


String scheduleTimes[10];       // Store up to 10 feeding times
int scheduleCount = 0;
String lastActivatedTime = "";  // Track last activated time to prevent re-triggering


int restPosition = 0;
int feedPosition = 90;


void setup() {
  Serial.begin(9600);


  pinMode(SERVO_PIN, OUTPUT);
  digitalWrite(SERVO_PIN, LOW);


  myRTC.updateTime();
  delay(1000);


  foodServo.attach(SERVO_PIN);
  foodServo.write(restPosition);


  // OPTIONAL: Set RTC time ONCE, then comment out!
  //myRTC.setDS1302Time(0, 5, 23, 7, 23, 3, 2025);  // sec, min, hour, DOW, day, month, year


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


  delay(1000);
}


void dispenseFood() {
  Serial.println("[ACTION] Moving servo to feed position...");
  foodServo.write(feedPosition);
  delay(5000);
  foodServo.write(restPosition);
  Serial.println("[ACTION] Dog Food dispensed.");
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


