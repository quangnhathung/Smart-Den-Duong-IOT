#include "LightingController.h"

#include <cmath>

using namespace ControlConfig;

const char *controlModeName(ControlMode mode) {
  return mode == ControlMode::Manual ? "MANUAL" : "AUTO";
}

const char *environmentName(Environment environment) {
  switch (environment) {
    case Environment::Day:
      return "DAY";
    case Environment::Twilight:
      return "TWILIGHT";
    case Environment::Night:
      return "NIGHT";
    default:
      return "UNKNOWN";
  }
}

const char *motionName(Motion motion) {
  switch (motion) {
    case Motion::Pedestrian:
      return "PEDESTRIAN";
    case Motion::Vehicle:
      return "VEHICLE";
    case Motion::Unknown:
      return "UNKNOWN";
    default:
      return "NONE";
  }
}

void LightingController::reset(uint32_t nowMs) {
  current = ControlState{};
  dimming.reset(nowMs);
  fault.reset(nowMs);
  sampleCount = 0;
  sampleIndex = 0;
  haveAnalogSequence = false;
  candidate = Environment::Unknown;
  candidateSinceMs = nowMs;
  manualSinceMs = nowMs;
  lastFaultCheckMs = nowMs;
  clearHold();
}

void LightingController::clearHold() {
  holdActive = false;
  holdLevel = 0;
}

bool LightingController::requestManual(int brightness, uint32_t nowMs) {
  if (brightness < 0 || brightness > MAX_BRIGHTNESS) {
    return false;
  }
  current.mode = ControlMode::Manual;
  current.brightnessTarget = static_cast<uint8_t>(brightness);
  manualSinceMs = nowMs;
  clearHold();
  return true;
}

void LightingController::requestAuto() {
  current.mode = ControlMode::Auto;
  clearHold();
}

const ControlState &LightingController::state() const {
  return current;
}

void LightingController::updateEnvironment(const ControlInput &input, uint32_t nowMs) {
  if (haveAnalogSequence && lastAnalogSequence == input.analogSequence) {
    return;
  }
  haveAnalogSequence = true;
  lastAnalogSequence = input.analogSequence;
  if (input.ldrAdc > ADC_MAX) {
    sampleCount = 0;
    sampleIndex = 0;
    candidate = Environment::Unknown;
    current.environment = Environment::Unknown;
    clearHold();
    return;
  }
  ldrSamples[sampleIndex] = input.ldrAdc;
  sampleIndex = (sampleIndex + 1) % LDR_FILTER_SAMPLES;
  if (sampleCount < LDR_FILTER_SAMPLES) {
    ++sampleCount;
  }
  if (sampleCount < LDR_FILTER_SAMPLES) {
    return;
  }
  uint32_t sum = 0;
  for (uint16_t sample : ldrSamples) {
    sum += sample;
  }
  current.filteredLdrAdc = static_cast<uint16_t>(sum / LDR_FILTER_SAMPLES);
  const uint16_t adc = current.filteredLdrAdc;
  Environment next = current.environment;
  switch (current.environment) {
    case Environment::Day:
      next = adc >= NIGHT_ENTER_MIN ? Environment::Night : (adc >= DAY_EXIT_MIN ? Environment::Twilight : Environment::Day);
      break;
    case Environment::Twilight:
      next = adc <= DAY_ENTER_MAX ? Environment::Day : (adc >= NIGHT_ENTER_MIN ? Environment::Night : Environment::Twilight);
      break;
    case Environment::Night:
      next = adc <= DAY_ENTER_MAX ? Environment::Day : (adc <= NIGHT_EXIT_MAX ? Environment::Twilight : Environment::Night);
      break;
    default:
      next = adc < INITIAL_DAY_THRESHOLD ? Environment::Day : (adc <= INITIAL_NIGHT_THRESHOLD ? Environment::Twilight : Environment::Night);
      break;
  }
  if (next == current.environment) {
    candidate = current.environment;
    candidateSinceMs = nowMs;
  } else if (next != candidate) {
    candidate = next;
    candidateSinceMs = nowMs;
  } else if (nowMs - candidateSinceMs >= ENVIRONMENT_CONFIRM_MS) {
    current.environment = candidate;
  }
}

uint8_t LightingController::autoTarget(const ControlInput &input, uint32_t nowMs) {
  if (current.environment == Environment::Day || current.environment == Environment::Unknown) {
    clearHold();
    return current.environment == Environment::Day ? 0 : UNKNOWN_BRIGHTNESS;
  }
  const uint8_t base = current.environment == Environment::Night ? NIGHT_BRIGHTNESS : TWILIGHT_BRIGHTNESS;
  if (holdActive && nowMs - holdSinceMs >= HOLD_MS) {
    clearHold();
  }
  if (input.pirMotion) {
    const uint8_t requested = current.motion == Motion::Pedestrian ? PEDESTRIAN_BRIGHTNESS : MAX_BRIGHTNESS;
    if (requested > holdLevel) {
      holdLevel = requested;
    }
    holdSinceMs = nowMs;
    holdActive = true;
  }
  return holdActive && holdLevel > base ? holdLevel : base;
}

const ControlState &LightingController::update(const ControlInput &input, uint32_t nowMs, bool mqttConnected) {
  updateEnvironment(input, nowMs);
  const bool validDistance = input.distanceValid && std::isfinite(input.distanceCm) && input.distanceCm > 0;
  current.motion =
    !input.pirMotion ? Motion::None : (!validDistance ? Motion::Unknown : (input.distanceCm < VEHICLE_DISTANCE_CM ? Motion::Vehicle : Motion::Pedestrian));
  if (current.mode == ControlMode::Manual && (!mqttConnected || nowMs - manualSinceMs >= MANUAL_TIMEOUT_MS)) {
    requestAuto();
  }
  if (current.mode == ControlMode::Auto) {
    current.brightnessTarget = autoTarget(input, nowMs);
  }
  current.brightnessApplied = dimming.update(current.brightnessTarget, nowMs);
  fault.observeBrightness(current.brightnessApplied, nowMs);
  if (nowMs - lastFaultCheckMs >= FAULT_INTERVAL_MS) {
    lastFaultCheckMs = nowMs;
    current.openLoad = fault.update(current.brightnessApplied, input.currentAdc, nowMs);
  }
  return current;
}
