#pragma once

#include <stdint.h>

class FaultDetector {
public:
  void reset(uint32_t nowMs);
  void observeBrightness(uint8_t applied, uint32_t nowMs);
  bool update(uint8_t applied, uint16_t currentAdc, uint32_t nowMs);

private:
  uint8_t lastApplied = 0;
  uint32_t stableSinceMs = 0;
  uint32_t conditionSinceMs = 0;
  bool conditionActive = false;
  bool openLoad = false;
};
