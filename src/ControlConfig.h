#pragma once

#include <stdint.h>

// SRS 5.3-5.8. ADC is raw 12-bit; brightness is integer percent.
namespace ControlConfig {
constexpr uint16_t ADC_MAX = 4095;
constexpr uint8_t LDR_FILTER_SAMPLES = 5;
constexpr uint16_t INITIAL_DAY_THRESHOLD = 1200;
constexpr uint16_t INITIAL_NIGHT_THRESHOLD = 2600;
constexpr uint16_t DAY_ENTER_MAX = 1100;
constexpr uint16_t DAY_EXIT_MIN = 1300;
constexpr uint16_t NIGHT_ENTER_MIN = 2700;
constexpr uint16_t NIGHT_EXIT_MAX = 2500;
constexpr uint32_t ENVIRONMENT_CONFIRM_MS = 1000;
constexpr uint8_t UNKNOWN_BRIGHTNESS = 50;
constexpr uint8_t TWILIGHT_BRIGHTNESS = 50;
constexpr uint8_t NIGHT_BRIGHTNESS = 25;
constexpr uint8_t PEDESTRIAN_BRIGHTNESS = 70;
constexpr uint8_t MAX_BRIGHTNESS = 100;
constexpr float VEHICLE_DISTANCE_CM = 100.0f;
constexpr uint32_t HOLD_MS = 5000;
constexpr uint32_t MANUAL_TIMEOUT_MS = 60000;
constexpr uint32_t DIMMING_INTERVAL_MS = 20;
constexpr uint8_t DIMMING_STEP = 2;
constexpr uint32_t FAULT_INTERVAL_MS = 100;
constexpr uint8_t FAULT_MIN_BRIGHTNESS = 20;
constexpr uint32_t FAULT_STABLE_MS = 1000;
constexpr uint8_t OPEN_LOAD_PERCENT = 10;
constexpr uint8_t RECOVERY_PERCENT = 20;
constexpr uint32_t OPEN_LOAD_CONFIRM_MS = 2000;
constexpr uint32_t RECOVERY_CONFIRM_MS = 3000;
} // namespace ControlConfig
