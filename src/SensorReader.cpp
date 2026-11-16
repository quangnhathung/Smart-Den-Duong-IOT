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
bool firstDistance = true;
volatile bool echoPending = false;
volatile bool echoHigh = false;
volatile bool echoComplete = false;
volatile uint32_t echoRiseUs = 0;
volatile uint32_t echoDurationUs = 0;
volatile uint32_t triggerSinceUs = 0;

void IRAM_ATTR captureEcho() {
  if (!echoPending) {
    return;
  }
  const uint32_t nowUs = micros();
  if (nowUs - triggerSinceUs >= ECHO_TIMEOUT_US) {
    echoDurationUs = 0;
    echoComplete = true;
    echoPending = false;
    return;
  }
  if (digitalRead(ECHO_PIN) == HIGH) {
    echoRiseUs = nowUs;
    echoHigh = true;
  } else if (echoHigh) {
    echoDurationUs = nowUs - echoRiseUs;
    echoComplete = true;
    echoPending = false;
  }
}

void readAnalog() {
  snapshot.ldrAdc = analogRead(LDR_PIN);
  snapshot.currentAdc = analogRead(CURRENT_PIN);
  ++snapshot.analogSequence;
}

void updateDistance(uint32_t nowMs) {
  // Only short critical sections; no busy wait for ECHO. Ignore late edges after timeout.
  const uint32_t nowUs = micros();
  noInterrupts();
  const bool complete = echoComplete;
  const uint32_t durationUs = echoDurationUs;
  const bool timedOut = echoPending && nowUs - triggerSinceUs >= ECHO_TIMEOUT_US;
  if (complete || timedOut) {
    echoComplete = false;
    echoPending = false;
    echoHigh = false;
  }
  const bool pending = echoPending;
  interrupts();
  if (complete || timedOut) {
    snapshot.distanceValid = complete && durationUs > 0 && durationUs <= ECHO_TIMEOUT_US;
    snapshot.distanceCm = snapshot.distanceValid ? durationUs / 58.0f : 0.0f;
  }
  if (pending || (!firstDistance && nowMs - lastDistanceMs < DISTANCE_INTERVAL_MS)) {
    return;
  }
  firstDistance = false;
  lastDistanceMs = nowMs;
  noInterrupts();
  echoHigh = false;
  echoComplete = false;
  echoDurationUs = 0;
  triggerSinceUs = micros();
  echoPending = true;
  interrupts();
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
}
} // namespace

void setupSensors() {
  pinMode(LDR_PIN, INPUT);
  pinMode(CURRENT_PIN, INPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT_PULLDOWN);
  noInterrupts();
  echoPending = false;
  echoHigh = false;
  echoComplete = false;
  interrupts();
  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), captureEcho, CHANGE);
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
  lastDistanceMs = now;
  firstDistance = true;
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
  updateDistance(nowMs);
}

const SensorSnapshot &getSensorSnapshot() {
  return snapshot;
}
