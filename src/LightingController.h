#pragma once

#include "ControlTypes.h"
#include "ControlConfig.h"
#include "DimmingController.h"
#include "FaultDetector.h"

class LightingController {
public:
  void reset(uint32_t nowMs);
  const ControlState &update(const ControlInput &input, uint32_t nowMs, bool mqttConnected);
  bool requestManual(int brightness, uint32_t nowMs);
  void requestAuto();
  const ControlState &state() const;

private:
  void updateEnvironment(const ControlInput &input, uint32_t nowMs);
  uint8_t autoTarget(const ControlInput &input, uint32_t nowMs);
  void clearHold();

  ControlState current;
  DimmingController dimming;
  FaultDetector fault;
  uint16_t ldrSamples[ControlConfig::LDR_FILTER_SAMPLES] = {};
  uint8_t sampleCount = 0;
  uint8_t sampleIndex = 0;
  uint32_t lastAnalogSequence = 0;
  bool haveAnalogSequence = false;
  Environment candidate = Environment::Unknown;
  uint32_t candidateSinceMs = 0;
  uint32_t manualSinceMs = 0;
  uint32_t lastFaultCheckMs = 0;
  uint32_t holdSinceMs = 0;
  uint8_t holdLevel = 0;
  bool holdActive = false;
};
