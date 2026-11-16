#include "FaultDetector.h"
#include "ControlConfig.h"

using namespace ControlConfig;

void FaultDetector::reset(uint32_t nowMs) {
  lastApplied = 0;
  stableSinceMs = nowMs;
  conditionSinceMs = nowMs;
  conditionActive = false;
  openLoad = false;
}

void FaultDetector::observeBrightness(uint8_t applied, uint32_t nowMs) {
  if (applied != lastApplied) {
    lastApplied = applied;
    stableSinceMs = nowMs;
    conditionActive = false;
  }
}

bool FaultDetector::update(uint8_t applied, uint16_t currentAdc, uint32_t nowMs) {
  observeBrightness(applied, nowMs);
  if (applied < FAULT_MIN_BRIGHTNESS || currentAdc > ADC_MAX || nowMs - stableSinceMs < FAULT_STABLE_MS) {
    conditionActive = false;
    return openLoad;
  }
  // I_sim / I_expected = current_adc / 4095, without float rounding at thresholds.
  const bool qualifying = openLoad ? currentAdc * 100U >= ADC_MAX * RECOVERY_PERCENT : currentAdc * 100U < ADC_MAX * OPEN_LOAD_PERCENT;
  if (!qualifying) {
    conditionActive = false;
  } else if (!conditionActive) {
    conditionActive = true;
    conditionSinceMs = nowMs;
  } else if (nowMs - conditionSinceMs >= (openLoad ? RECOVERY_CONFIRM_MS : OPEN_LOAD_CONFIRM_MS)) {
    openLoad = !openLoad;
    conditionActive = false;
  }
  return openLoad;
}
