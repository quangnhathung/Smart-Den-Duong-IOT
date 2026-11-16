#pragma once

#include <stdint.h>

constexpr uint8_t LOW = 0;
constexpr uint8_t HIGH = 1;
constexpr uint8_t INPUT = 1;
constexpr uint8_t OUTPUT = 3;
constexpr uint8_t INPUT_PULLDOWN = 9;
constexpr uint8_t CHANGE = 2;
#define IRAM_ATTR
enum adc_attenuation_t { ADC_11db };

unsigned long millis();
unsigned long micros();
void noInterrupts();
void interrupts();
void attachInterrupt(uint8_t pin, void (*handler)(), int mode);
constexpr uint8_t digitalPinToInterrupt(uint8_t pin) {
  return pin;
}
void pinMode(uint8_t pin, uint8_t mode);
void digitalWrite(uint8_t pin, uint8_t value);
int digitalRead(uint8_t pin);
uint16_t analogRead(uint8_t pin);
void analogReadResolution(uint8_t bits);
void analogSetPinAttenuation(uint8_t pin, adc_attenuation_t attenuation);
void delayMicroseconds(unsigned int duration);
unsigned long pulseIn(uint8_t pin, uint8_t state, unsigned long timeout);
