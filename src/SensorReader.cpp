#include "SensorReader.h"

#include <Arduino.h>

namespace {
constexpr uint8_t LDR_PIN = 34;
constexpr uint8_t CURRENT_PIN = 35;
constexpr uint8_t PIR_PIN = 27;
constexpr uint8_t TRIG_PIN = 18;
constexpr uint8_t ECHO_PIN = 19;
constexpr uint32_t ANALOG_INTERVAL_MS = 100;
constexpr uint32_t PIR_INTERVAL_MS = 20;
constexpr uint32_t DISTANCE_INTERVAL_MS = 200;
constexpr uint32_t ECHO_TIMEOUT_US = 30000;
SensorSnapshot snapshot = {};
uint32_t lastAnalogMs = 0;
uint32_t lastPirMs = 0;
uint32_t lastDistanceMs = 0;

void readAnalog() {
  snapshot.ldrAdc = analogRead(LDR_PIN);
  snapshot.currentAdc = analogRead(CURRENT_PIN);
}

void readDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  const unsigned long durationUs = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);
  snapshot.distanceValid = durationUs > 0;
  snapshot.distanceCm = snapshot.distanceValid ? durationUs / 58.0f : 0.0f;
}
} // namespace

void setupSensors() {
  pinMode(LDR_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT_PULLDOWN);
  digitalWrite(TRIG_PIN, LOW);
  analogReadResolution(12);
  analogSetPinAttenuation(LDR_PIN, ADC_11db);
  analogSetPinAttenuation(CURRENT_PIN, ADC_11db);
  snapshot = {};
  readAnalog();
  snapshot.pirMotion = digitalRead(PIR_PIN) == HIGH;
  const uint32_t now = millis();
  lastAnalogMs = now;
  lastPirMs = now;
  lastDistanceMs = now - DISTANCE_INTERVAL_MS;
}

void updateSensors(uint32_t nowMs) {
  if (nowMs - lastPirMs >= PIR_INTERVAL_MS) {
    lastPirMs = nowMs;
    snapshot.pirMotion = digitalRead(PIR_PIN) == HIGH;
  }
  if (nowMs - lastAnalogMs >= ANALOG_INTERVAL_MS) {
    lastAnalogMs = nowMs;
    readAnalog();
  }
  if (nowMs - lastDistanceMs >= DISTANCE_INTERVAL_MS) {
    lastDistanceMs = nowMs;
    readDistance();
  }
}

const SensorSnapshot &getSensorSnapshot() {
  return snapshot;
}
