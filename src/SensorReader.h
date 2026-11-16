#pragma once

#include <stdint.h>

struct SensorSnapshot {
  uint16_t ldrAdc;
  uint16_t currentAdc;
  bool pirMotion;
  float distanceCm; // Only meaningful when distanceValid is true.
  bool distanceValid;
  uint32_t analogSequence;
};

void setupSensors();
void updateSensors(uint32_t nowMs);
const SensorSnapshot &getSensorSnapshot();
