#pragma once

#include <stdint.h>

enum class ControlMode { Auto, Manual };
enum class Environment { Unknown, Day, Twilight, Night };
enum class Motion { None, Pedestrian, Vehicle, Unknown };

struct ControlInput {
  uint16_t ldrAdc = 0;
  uint16_t currentAdc = 0;
  bool pirMotion = false;
  bool distanceValid = false;
  float distanceCm = 0;
  uint32_t analogSequence = 0;
};

struct ControlState {
  ControlMode mode = ControlMode::Auto;
  Environment environment = Environment::Unknown;
  Motion motion = Motion::None;
  uint16_t filteredLdrAdc = 0;
  uint8_t brightnessTarget = 50;
  uint8_t brightnessApplied = 0;
  bool openLoad = false;
};

constexpr uint8_t brightnessToDuty(uint8_t percent) {
  return static_cast<uint8_t>((percent * 255U + 50U) / 100U);
}

const char *controlModeName(ControlMode mode);
const char *environmentName(Environment environment);
const char *motionName(Motion motion);
