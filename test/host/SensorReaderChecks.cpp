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
uint16_t lightValue = 1234;
uint16_t currentValue = 4095;
int pirValue = LOW;
unsigned long echoUs = 5800;
unsigned int analogReads = 0;
unsigned int pirReads = 0;
unsigned int distanceReads = 0;
uint8_t modes[40] = {};
std::vector<std::pair<uint8_t, uint8_t>> writes;
std::vector<unsigned int> pulseDelays;

void updateAt(uint32_t timeMs) {
  nowMs = timeMs;
  updateSensors(nowMs);
}
} // namespace

unsigned long millis() {
  return nowMs;
}
void pinMode(uint8_t pin, uint8_t mode) {
  modes[pin] = mode;
}
void digitalWrite(uint8_t pin, uint8_t value) {
  assert(pin == 18);
  writes.emplace_back(pin, value);
}
int digitalRead(uint8_t pin) {
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
}
unsigned long pulseIn(uint8_t pin, uint8_t state, unsigned long timeout) {
  assert(pin == 19 && state == HIGH && timeout == 30000);
  ++distanceReads;
  return echoUs;
}

int main() {
  setupSensors();
  assert(modes[34] == INPUT && modes[35] == INPUT && modes[27] == INPUT);
  assert(modes[18] == OUTPUT && modes[19] == INPUT_PULLDOWN);
  assert(!getSensorSnapshot().distanceValid);
  assert(getSensorSnapshot().ldrAdc == 1234 && getSensorSnapshot().currentAdc == 4095);
  updateAt(0);
  assert(distanceReads == 1 && getSensorSnapshot().distanceValid);
  assert(std::fabs(getSensorSnapshot().distanceCm - 100.0f) < 0.01f);
  assert(writes.size() == 4 && writes[1].second == LOW && writes[2].second == HIGH && writes[3].second == LOW);
  assert(pulseDelays.size() == 2 && pulseDelays[0] == 2 && pulseDelays[1] >= 10);
  pirValue = HIGH;
  lightValue = 42;
  currentValue = 2048;
  updateAt(19);
  assert(pirReads == 1 && analogReads == 2 && !getSensorSnapshot().pirMotion);
  updateAt(20);
  assert(pirReads == 2 && getSensorSnapshot().pirMotion);
  updateAt(99);
  assert(analogReads == 2 && getSensorSnapshot().ldrAdc == 1234);
  updateAt(100);
  assert(analogReads == 4 && getSensorSnapshot().ldrAdc == 42 && getSensorSnapshot().currentAdc == 2048);
  echoUs = 0;
  updateAt(199);
  assert(distanceReads == 1 && getSensorSnapshot().distanceValid);
  updateAt(200);
  assert(distanceReads == 2 && !getSensorSnapshot().distanceValid && getSensorSnapshot().distanceCm == 0.0f);
  echoUs = 23200;
  updateAt(400);
  assert(getSensorSnapshot().distanceValid && std::fabs(getSensorSnapshot().distanceCm - 400.0f) < 0.01f);
  echoUs = 116;
  updateAt(600);
  assert(std::fabs(getSensorSnapshot().distanceCm - 2.0f) < 0.01f);
  std::puts("PASS: pin setup, ADC/PIR scheduling, trigger pulse, 30 ms timeout, stale distance clearing and recovery at 2/100/400 cm");

  nowMs = std::numeric_limits<uint32_t>::max() - 50;
  setupSensors();
  updateAt(nowMs);
  const unsigned int beforeAnalog = analogReads;
  const unsigned int beforeDistance = distanceReads;
  const unsigned int beforePir = pirReads;
  pirValue = LOW;
  updateAt(std::numeric_limits<uint32_t>::max() - 31);
  assert(pirReads == beforePir);
  updateAt(std::numeric_limits<uint32_t>::max() - 30);
  assert(pirReads == beforePir + 1 && !getSensorSnapshot().pirMotion);
  updateAt(48);
  assert(analogReads == beforeAnalog);
  updateAt(49);
  assert(analogReads == beforeAnalog + 2);
  updateAt(148);
  assert(distanceReads == beforeDistance);
  updateAt(149);
  assert(distanceReads == beforeDistance + 1);
  std::puts("PASS: analog, PIR and distance schedules across uint32 millis wrap");
  std::puts("Host tests use mocked GPIO/ADC/echo; Wokwi electrical and live network behavior NOT verified.");
}
