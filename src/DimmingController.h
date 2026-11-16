#pragma once

#include <stdint.h>

class DimmingController {
public:
  void reset(uint32_t nowMs);
  uint8_t update(uint8_t target, uint32_t nowMs);

private:
  uint32_t lastStepMs = 0;
  uint8_t applied = 0;
};
