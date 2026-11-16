#pragma once

#include "../Arduino.h"
#include <cstdarg>
#include <cstdio>
#include <cstring>
#include <string>

struct FakeSerial {
  std::string input;
  std::string output;
  void begin(unsigned long) {}
  int available() {
    return static_cast<int>(input.size());
  }
  int read() {
    if (input.empty()) {
      return -1;
    }
    const unsigned char value = input[0];
    input.erase(0, 1);
    return value;
  }
  int printf(const char *format, ...) {
    char text[512];
    va_list args;
    va_start(args, format);
    const int length = vsnprintf(text, sizeof(text), format, args);
    va_end(args);
    output += text;
    return length;
  }
  void println(const char *text) {
    output += std::string(text) + "\r\n";
  }
};
extern FakeSerial Serial;
bool ledcAttach(uint8_t pin, uint32_t frequency, uint8_t resolution);
bool ledcWrite(uint8_t pin, uint32_t duty);
void delay(unsigned long duration);
constexpr int pdPASS = 1;
constexpr unsigned long pdMS_TO_TICKS(unsigned long milliseconds) {
  return milliseconds;
}
int xTaskCreatePinnedToCore(void (*task)(void *), const char *name, unsigned long stack, void *argument, int priority, void *handle, int core);
void vTaskDelay(unsigned long ticks);

struct portMUX_TYPE {};
#define portMUX_INITIALIZER_UNLOCKED                                                                                                                           \
  {                                                                                                                                                            \
  }
inline void portENTER_CRITICAL(portMUX_TYPE *) {}
inline void portEXIT_CRITICAL(portMUX_TYPE *) {}
