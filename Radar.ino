#include <Arduino.h>
#include <ESP32Servo.h>

#define delayTime 30
#define servoPin 13
#define trigPin 12
#define echoPin 14

int currPos = 0;
int servoDirection = 2;

float duration_us, distance_cm;

Servo servo;

void setup() {

  Serial.begin(115200);

  ESP32PWM::allocateTimer(0);
  servo.setPeriodHertz(50);
  servo.attach(servoPin, 500, 2400);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration_us = pulseIn(echoPin, HIGH);
  distance_cm = 0.017 * duration_us;

  Serial.print((int)distance_cm);
  Serial.print(", ");
  Serial.println(currPos);

  servo.write(currPos);
  currPos += servoDirection;

  if (currPos >= 180) {
    currPos = 180;
    servoDirection = -2;
  } else if (currPos <= 0) {
    currPos = 0;
    servoDirection = 2;
  }

  delay(delayTime);
}