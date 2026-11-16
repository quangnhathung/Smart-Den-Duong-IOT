#pragma once
#include <Arduino.h>
#include <stdint.h>
inline int64_t fakeEspTimeUs = -1;
inline int64_t esp_timer_get_time() {
  return fakeEspTimeUs >= 0 ? fakeEspTimeUs : static_cast<int64_t>(millis()) * 1000;
}
