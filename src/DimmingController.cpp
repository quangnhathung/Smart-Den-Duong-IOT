#include "DimmingController.h"
#include "ControlConfig.h"

using namespace ControlConfig;

void DimmingController::reset(uint32_t nowMs) {
  applied = 0;
  lastStepMs = nowMs;
}

uint8_t DimmingController::update(uint8_t target, uint32_t nowMs) {
  if (nowMs - lastStepMs < DIMMING_INTERVAL_MS) {
    return applied;
  }
  lastStepMs = nowMs;
  if (target > MAX_BRIGHTNESS) {
    target = MAX_BRIGHTNESS;
  }
  // Never catch up in a burst after a delayed loop: at most 2 points per step.
  if (applied < target) {
    applied += target - applied > DIMMING_STEP ? DIMMING_STEP : target - applied;
  } else if (applied > target) {
    applied -= applied - target > DIMMING_STEP ? DIMMING_STEP : applied - target;
  }
  return applied;
}
