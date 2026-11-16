#include "SensorReader.h"
#include <Arduino.h>

#include <cassert>
#include <cmath>
#include <cstdio>
#include <limits>
#include <utility>
#include <vector>

namespace {
uint32_t nowMs = 0;
uint32_t nowUs = 0;
uint16_t lightValue = 1234;
uint16_t currentValue = 4095;
int pirValue = LOW;
int echoValue = LOW;
unsigned int analogReads = 0;
unsigned int pirReads = 0;
uint8_t modes[40] = {};
std::vector<std::pair<uint8_t, uint8_t>> writes;
std::vector<unsigned int> pulseDelays;
void (*echoHandler)() = nullptr;

void updateAt(uint32_t timeMs) {
  nowMs = timeMs;
  nowUs = timeMs * 1000U;
  updateSensors(nowMs);
}

void edge(int value, uint32_t timeUs) {
  nowUs = timeUs;
  echoValue = value;
  assert(echoHandler != nullptr);
  echoHandler();
}

void measure(uint32_t startMs, uint32_t widthUs, float expectedCm) {
  updateAt(startMs);
  edge(HIGH, startMs * 1000U + 100);
  edge(LOW, startMs * 1000U + 100 + widthUs);
  nowMs = startMs + (widthUs + 1100) / 1000;
  updateSensors(nowMs);
  assert(getSensorSnapshot().distanceValid);
  assert(std::fabs(getSensorSnapshot().distanceCm - expectedCm) < 0.01f);
}
} // namespace

unsigned long millis() {
  return nowMs;
}
unsigned long micros() {
  return nowUs;
}
void noInterrupts() {}
void interrupts() {}
void attachInterrupt(uint8_t pin, void (*handler)(), int mode) {
  assert(pin == 19 && mode == CHANGE);
  echoHandler = handler;
}
void pinMode(uint8_t pin, uint8_t mode) {
  modes[pin] = mode;
}
void digitalWrite(uint8_t pin, uint8_t value) {
  assert(pin == 18);
  writes.emplace_back(pin, value);
}
int digitalRead(uint8_t pin) {
  if (pin == 19) {
    return echoValue;
  }
  assert(pin == 27);
  ++pirReads;
  return pirValue;
}
uint16_t analogRead(uint8_t pin) {
  assert(pin == 34 || pin == 35);
  ++analogReads;
  return pin == 34 ? lightValue : currentValue;
}
void analogReadResolution(uint8_t bits) {
  assert(bits == 12);
}
void analogSetPinAttenuation(uint8_t pin, adc_attenuation_t attenuation) {
  assert((pin == 34 || pin == 35) && attenuation == ADC_11db);
}
void delayMicroseconds(unsigned int duration) {
  pulseDelays.push_back(duration);
  nowUs += duration;
}
unsigned long pulseIn(uint8_t, uint8_t, unsigned long) {
  assert(false && "blocking pulseIn must never be used");
  return 0;
}

int main() {
  setupSensors();
  assert(modes[34] == INPUT && modes[35] == INPUT && modes[27] == INPUT);
  assert(modes[18] == OUTPUT && modes[19] == INPUT_PULLDOWN);
  assert(getSensorSnapshot().analogSequence == 1 && !getSensorSnapshot().distanceValid);
  measure(0, 5800, 100);
  assert(writes.size() == 4 && writes[1].second == LOW && writes[2].second == HIGH && writes[3].second == LOW);
  assert(pulseDelays.size() == 2 && pulseDelays[0] == 2 && pulseDelays[1] == 10);
  pirValue = HIGH;
  lightValue = 42;
  currentValue = 2048;
  updateAt(19);
  assert(pirReads == 1 && analogReads == 2);
  updateAt(20);
  assert(getSensorSnapshot().pirMotion && analogReads == 2);
  updateAt(100);
  assert(analogReads == 4 && getSensorSnapshot().ldrAdc == 42 && getSensorSnapshot().currentAdc == 2048);
  assert(getSensorSnapshot().analogSequence == 2);
  updateAt(200);
  updateAt(229);
  assert(getSensorSnapshot().distanceValid);
  updateAt(230);
  assert(!getSensorSnapshot().distanceValid && getSensorSnapshot().distanceCm == 0);
  edge(HIGH, 231000);
  edge(LOW, 232000);
  updateAt(233);
  assert(!getSensorSnapshot().distanceValid);
  measure(400, 23200, 400);
  measure(600, 116, 2);
  updateAt(800);
  edge(LOW, 800100);
  updateAt(830);
  assert(!getSensorSnapshot().distanceValid);
  updateAt(1000);
  edge(HIGH, 1031000); // expired edge before foreground has had a chance to process timeout
  edge(LOW, 1032000);
  updateSensors(1032);
  assert(!getSensorSnapshot().distanceValid);
  nowMs = 1000;
  nowUs = std::numeric_limits<uint32_t>::max() - 100;
  setupSensors();
  updateSensors(nowMs);
  const uint32_t rise = std::numeric_limits<uint32_t>::max() - 50;
  edge(HIGH, rise);
  edge(LOW, rise + 116U);
  updateSensors(1001);
  assert(getSensorSnapshot().distanceValid && std::fabs(getSensorSnapshot().distanceCm - 2) < 0.01f);
  nowMs = std::numeric_limits<uint32_t>::max() - 50;
  nowUs = nowMs * 1000U;
  setupSensors();
  updateSensors(nowMs);
  const unsigned int beforeAnalog = analogReads;
  const unsigned int beforePir = pirReads;
  updateAt(nowMs + 19U);
  assert(pirReads == beforePir);
  updateAt(std::numeric_limits<uint32_t>::max() - 30U);
  assert(pirReads == beforePir + 1);
  updateAt(49);
  assert(analogReads == beforeAnalog + 2);
  std::puts(
    "PASS sensors: async ECHO, 12us TRIG, 30ms timeout/late edges, invalidation/recovery 2/100/400cm, ADC/PIR scheduling, micros/millis wrap; no pulseIn");
}
