#include "LightingController.h"

#include <cassert>
#include <cstdio>
#include <initializer_list>
#include <limits>

namespace {
struct Rig {
  LightingController controller;
  ControlInput input;
  uint32_t now = 0;
  uint32_t lastAnalog = 0;
  bool connected = true;

  explicit Rig(uint32_t start = 0) : now(start), lastAnalog(start) {
    input.ldrAdc = 3000;
    input.currentAdc = 4095;
    input.distanceValid = true;
    input.distanceCm = 150;
    input.analogSequence = 1;
    controller.reset(now);
    controller.update(input, now, connected);
  }

  const ControlState &state() const {
    return controller.state();
  }

  void tick(uint32_t duration = 20) {
    now += duration;
    if (now - lastAnalog >= 100) {
      lastAnalog = now;
      ++input.analogSequence;
    }
    controller.update(input, now, connected);
  }

  void advance(uint32_t duration) {
    for (uint32_t elapsed = 0; elapsed < duration; elapsed += 20) {
      tick();
    }
  }

  void settle(uint16_t adc) {
    input.ldrAdc = adc;
    advance(1600);
  }
};

void checkEnvironment() {
  Rig rig;
  assert(rig.state().mode == ControlMode::Auto && rig.state().environment == Environment::Unknown);
  assert(rig.state().brightnessTarget == 50);
  rig.advance(1380);
  assert(rig.state().environment == Environment::Unknown);
  rig.tick();
  assert(rig.state().environment == Environment::Night && rig.state().brightnessTarget == 25);
  rig.settle(1000);
  assert(rig.state().environment == Environment::Day && rig.state().brightnessTarget == 0);
  rig.settle(1299);
  assert(rig.state().environment == Environment::Day);
  rig.settle(1300);
  assert(rig.state().environment == Environment::Twilight && rig.state().brightnessTarget == 50);
  rig.settle(1101);
  assert(rig.state().environment == Environment::Twilight);
  rig.settle(1100);
  assert(rig.state().environment == Environment::Day);
  rig.settle(2700);
  assert(rig.state().environment == Environment::Night);
  rig.settle(2501);
  assert(rig.state().environment == Environment::Night);
  rig.settle(2500);
  assert(rig.state().environment == Environment::Twilight);
  rig.settle(2699);
  assert(rig.state().environment == Environment::Twilight);
  rig.settle(2700);
  assert(rig.state().environment == Environment::Night);
  rig.settle(1000);
  rig.input.ldrAdc = 3000;
  rig.advance(1000);
  assert(rig.state().environment == Environment::Day);
  rig.input.ldrAdc = 1000;
  rig.advance(500);
  rig.input.ldrAdc = 3000;
  rig.advance(1000);
  assert(rig.state().environment == Environment::Day); // candidate interrupted; no accumulated dwell
  rig.advance(600);
  assert(rig.state().environment == Environment::Night);
  rig.input.ldrAdc = 5000;
  rig.advance(100);
  assert(rig.state().environment == Environment::Unknown && rig.state().brightnessTarget == 50);
  Rig noNewSample;
  noNewSample.controller.update(noNewSample.input, 5000, true);
  assert(noNewSample.state().environment == Environment::Unknown); // don't count loop calls as samples
  for (uint16_t initial : {uint16_t(1199), uint16_t(1200), uint16_t(2600), uint16_t(2601)}) {
    Rig boundary;
    boundary.settle(initial);
    const Environment expected = initial < 1200 ? Environment::Day : (initial <= 2600 ? Environment::Twilight : Environment::Night);
    assert(boundary.state().environment == expected);
  }
  std::puts("PASS environment: 5 fresh samples, UNKNOWN startup, initial boundaries, hysteresis, 1s dwell, direct jumps, invalid ADC");
}

void checkAutoHoldAndManual() {
  Rig rig;
  rig.settle(3000);
  rig.input.distanceCm = 50;
  rig.tick();
  assert(rig.state().motion == Motion::None && rig.state().brightnessTarget == 25);
  rig.input.pirMotion = true;
  rig.input.distanceCm = 100;
  rig.tick();
  assert(rig.state().motion == Motion::Pedestrian && rig.state().brightnessTarget == 70);
  rig.input.distanceCm = 99.9f;
  rig.tick();
  assert(rig.state().motion == Motion::Vehicle && rig.state().brightnessTarget == 100);
  rig.input.distanceCm = 150;
  rig.tick();
  assert(rig.state().brightnessTarget == 100); // lower event must not shorten high hold
  rig.input.pirMotion = false;
  rig.advance(4980);
  assert(rig.state().brightnessTarget == 100);
  rig.tick();
  assert(rig.state().brightnessTarget == 25 && rig.state().motion == Motion::None);
  for (float invalid : {0.0f, -1.0f, std::numeric_limits<float>::quiet_NaN(), std::numeric_limits<float>::infinity()}) {
    rig.input.pirMotion = true;
    rig.input.distanceCm = invalid;
    rig.tick();
    assert(rig.state().motion == Motion::Unknown && rig.state().brightnessTarget == 100);
  }
  rig.input.distanceCm = 100;
  rig.input.distanceValid = false;
  rig.tick();
  assert(rig.state().motion == Motion::Unknown && rig.state().brightnessTarget == 100);
  rig.settle(1000);
  assert(rig.state().brightnessTarget == 0); // DAY wins even with motion
  assert(rig.controller.requestManual(80, rig.now));
  rig.tick();
  assert(rig.state().mode == ControlMode::Manual && rig.state().brightnessTarget == 80);
  assert(!rig.controller.requestManual(-1, rig.now) && !rig.controller.requestManual(101, rig.now));
  assert(rig.state().brightnessTarget == 80);
  rig.controller.requestAuto();
  rig.input.pirMotion = false;
  rig.settle(3000);
  assert(rig.state().brightnessTarget == 25); // old hold was cancelled
  assert(rig.controller.requestManual(0, rig.now));
  rig.tick(59999);
  assert(rig.state().mode == ControlMode::Manual);
  rig.tick(1);
  assert(rig.state().mode == ControlMode::Auto);
  assert(rig.controller.requestManual(100, rig.now));
  rig.tick(59000);
  assert(rig.controller.requestManual(81, rig.now));
  rig.tick(1000);
  assert(rig.state().mode == ControlMode::Manual && rig.state().brightnessTarget == 81);
  rig.connected = false;
  rig.tick();
  assert(rig.state().mode == ControlMode::Auto && rig.state().brightnessTarget == 25);
  rig.connected = true;
  rig.tick();
  assert(rig.state().mode == ControlMode::Auto);
  rig.input.pirMotion = true;
  rig.input.distanceValid = true;
  rig.input.distanceCm = 150;
  rig.settle(2000);
  assert(rig.state().brightnessTarget == 70);
  rig.input.pirMotion = false;
  rig.advance(5000);
  assert(rig.state().brightnessTarget == 50);
  rig.settle(3000);
  rig.input.pirMotion = true;
  rig.input.distanceCm = 50;
  rig.tick();
  assert(rig.state().brightnessTarget == 100);
  rig.controller.requestManual(80, rig.now);
  rig.input.pirMotion = false;
  rig.controller.requestAuto();
  rig.tick();
  assert(rig.state().brightnessTarget == 25); // explicit AUTO must not revive pre-MANUAL hold
  rig.controller.requestManual(81, rig.now);
  rig.settle(1000);
  assert(rig.state().environment == Environment::Day && rig.state().brightnessTarget == 81);
  std::puts("PASS AUTO/MANUAL: PIR gate, 100cm boundary, invalid distance, max hold/expiry, DAY priority, manual range/refresh/60s/offline, no stale hold");
}

void checkDimmingAndFault() {
  DimmingController dimming;
  dimming.reset(0);
  assert(dimming.update(100, 19) == 0);
  assert(dimming.update(100, 20) == 2);
  assert(dimming.update(100, 20) == 2);
  assert(dimming.update(100, 5000) == 4); // no catch-up jump
  for (uint32_t now = 5020; now <= 5260; now += 20) {
    dimming.update(25, now);
  }
  assert(dimming.update(25, 5280) == 25);
  assert(dimming.update(24, 5300) == 24);
  assert(brightnessToDuty(0) == 0 && brightnessToDuty(25) == 64 && brightnessToDuty(50) == 128);
  assert(brightnessToDuty(70) == 179 && brightnessToDuty(100) == 255);
  FaultDetector fault;
  fault.reset(0);
  assert(!fault.update(20, 0, 0));
  assert(!fault.update(20, 0, 999));
  assert(!fault.update(20, 0, 1000));
  assert(!fault.update(20, 0, 2999));
  assert(fault.update(20, 0, 3000));
  assert(fault.update(0, 4095, 5000)); // off must not clear fault
  assert(fault.update(20, 819, 6000));
  assert(fault.update(20, 819, 7000));
  assert(fault.update(20, 818, 9000)); // breaks recovery
  assert(fault.update(20, 819, 9100));
  assert(fault.update(20, 819, 12099));
  assert(!fault.update(20, 819, 12100));
  assert(!fault.update(20, 410, 13000)); // >=10% does not trigger
  assert(!fault.update(20, 409, 14000));
  assert(!fault.update(20, 5000, 15000)); // invalid ADC resets confirmation
  assert(!fault.update(20, 409, 16000));
  assert(!fault.update(21, 409, 17999)); // dimming interrupts stability
  assert(!fault.update(21, 409, 18999));
  assert(!fault.update(21, 409, 20998));
  assert(fault.update(21, 409, 20999));
  fault.reset(0);
  fault.update(25, 0, 0);
  fault.update(25, 0, 1000);
  fault.observeBrightness(26, 1500);
  fault.observeBrightness(25, 1540); // brightness changed between two 100ms fault samples
  assert(!fault.update(25, 0, 3000));
  assert(fault.update(25, 0, 5000));
  Rig rig;
  rig.settle(3000);
  rig.controller.requestManual(80, rig.now);
  rig.input.currentAdc = 0;
  rig.advance(5000);
  assert(rig.state().openLoad && rig.state().brightnessApplied == 80); // fault doesn't shut PWM off
  rig.controller.requestAuto();
  rig.tick();
  assert(rig.state().openLoad); // mode change doesn't clear
  std::puts("PASS dimming/fault: 20ms/2-point limit, odd targets, duty mapping, stable1s, detect2s/recover3s, thresholds, invalid ADC, persistent fault");
}

void checkWrap() {
  Rig rig(std::numeric_limits<uint32_t>::max() - 1000U);
  rig.settle(3000);
  assert(rig.state().environment == Environment::Night);
  rig.controller.requestManual(80, rig.now);
  rig.tick(59999);
  assert(rig.state().mode == ControlMode::Manual);
  rig.tick(1);
  assert(rig.state().mode == ControlMode::Auto);
  FaultDetector fault;
  const uint32_t start = std::numeric_limits<uint32_t>::max() - 1500U;
  fault.reset(start);
  fault.update(25, 0, start);
  fault.update(25, 0, start + 1000U);
  assert(fault.update(25, 0, start + 3000U));
  rig.controller.reset(std::numeric_limits<uint32_t>::max() - 2000U);
  rig.now = std::numeric_limits<uint32_t>::max() - 2000U;
  rig.lastAnalog = rig.now;
  rig.settle(3000);
  rig.input.pirMotion = true;
  rig.input.distanceCm = 50;
  rig.tick();
  rig.input.pirMotion = false;
  rig.advance(4980);
  assert(rig.state().brightnessTarget == 100);
  rig.tick();
  assert(rig.state().brightnessTarget == 25);
  std::puts("PASS wrap: filter/dwell, MANUAL deadline, hold and fault across uint32 rollover");
}
} // namespace

int main() {
  checkEnvironment();
  checkAutoHoldAndManual();
  checkDimmingAndFault();
  checkWrap();
}
