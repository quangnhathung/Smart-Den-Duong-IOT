#include "FirmwareApp.h"
#include "Connectivity.h"
#include "MqttMailbox.h"
#include "LocalControlCommand.h"
#include "SensorReader.h"
#include <Arduino.h>

#include <cassert>
#include <cstdio>
#include <string>

FakeSerial Serial;
namespace {
uint32_t appNow = 0;
uint32_t lastSample = 0;
SensorSnapshot sensors = {};
bool connected = true;
uint32_t losses = 0;
unsigned int connectivityStarts = 0;
MqttMailbox appMailbox;
MqttProtocol::TelemetrySnapshot latestSnapshot;
void enqueueRemote(const MqttProtocol::RemoteCommand &command) {
  assert(appMailbox.enqueue(command));
}
MqttProtocol::CommandResult popResult() {
  MqttProtocol::CommandResult result;
  assert(appMailbox.peekResult(result));
  appMailbox.popResult();
  return result;
}
unsigned int pwmWrites = 0;
uint32_t lastDuty = 0;
uint32_t lastWriteMs = 0;
bool haveWrite = false;

void runFor(uint32_t duration) {
  const uint32_t start = appNow;
  while (appNow - start < duration) {
    loopFirmware();
  }
}

void command(const std::string &text) {
  Serial.input += text;
  runFor(100);
}
} // namespace

unsigned long millis() {
  return appNow;
}
void delay(unsigned long duration) {
  assert(duration == 1);
  appNow += duration;
}
bool ledcAttach(uint8_t pin, uint32_t frequency, uint8_t resolution) {
  assert(pin == 26 && frequency == 5000 && resolution == 8);
  return true;
}
bool ledcWrite(uint8_t pin, uint32_t duty) {
  assert(pin == 26 && duty <= 255);
  if (haveWrite) {
    assert(appNow - lastWriteMs >= 20);
    const int difference = static_cast<int>(duty) - static_cast<int>(lastDuty);
    assert(difference >= -6 && difference <= 6);
  }
  haveWrite = true;
  lastWriteMs = appNow;
  lastDuty = duty;
  ++pwmWrites;
  return true;
}
bool startConnectivity() {
  ++connectivityStarts;
  return true;
}
bool isMqttConnected() {
  return connected;
}
uint32_t mqttDisconnectCount() {
  return losses;
}
const char *mqttBootId() {
  return "b7e28a10";
}
uint64_t firmwareUptimeMs() {
  return appNow;
}
void updateMqttSnapshot(const MqttProtocol::TelemetrySnapshot &snapshot) {
  latestSnapshot = snapshot;
}
bool takeRemoteCommand(MqttProtocol::RemoteCommand &command) {
  return appMailbox.takeCommand(command);
}
bool completeRemoteCommand(const MqttProtocol::CommandResult &result) {
  return appMailbox.complete(result);
}
void setupSensors() {
  sensors.ldrAdc = 1000;
  sensors.currentAdc = 4095;
  sensors.distanceCm = 150;
  sensors.distanceValid = true;
  sensors.analogSequence = 1;
}
void updateSensors(uint32_t nowMs) {
  if (nowMs - lastSample >= 100) {
    ++sensors.analogSequence;
    lastSample = nowMs;
  }
}
const SensorSnapshot &getSensorSnapshot() {
  return sensors;
}

int main() {
  LocalControlCommand parsed;
  assert(parseLocalControlCommand("AUTO", parsed) && !parsed.manual);
  assert(parseLocalControlCommand("MANUAL 80", parsed) && parsed.manual && parsed.brightness == 80);
  for (const char *bad : {"MANUAL", "MANUAL ", "MANUAL -1", "MANUAL 101", "MANUAL 80x", "MANUAL 1.5", "MANUAL 999999", "AUTO x", ""}) {
    assert(!parseLocalControlCommand(bad, parsed));
  }
  setupFirmware();
  assert(connectivityStarts == 1 && pwmWrites == 1 && lastDuty == 0);
  runFor(3000);
  assert(Serial.output.find("mode=AUTO environment=DAY") != std::string::npos);
  assert(lastDuty == 0);
  const unsigned int dayWrites = pwmWrites;
  runFor(6000);
  assert(pwmWrites == dayWrites); // no diagnostic PWM cycling
  command("MANUAL 80\r\n");
  runFor(1100);
  assert(lastDuty == 204 && Serial.output.find("mode=MANUAL") != std::string::npos);
  command("MANUAL 101\n");
  runFor(100);
  assert(lastDuty == 204 && Serial.output.find("accepted=0") != std::string::npos);
  command(std::string(100, 'X') + "AUTO\n");
  assert(lastDuty == 204); // overflow must not execute a truncated suffix
  command(std::string("AUTO\0garbage\n", 13));
  assert(lastDuty == 204); // embedded NUL must not turn a malformed line into AUTO
  command("AUTO\n");
  runFor(1000);
  assert(lastDuty == 0);
  sensors.ldrAdc = 3000;
  runFor(2200);
  assert(lastDuty == 64);
  sensors.pirMotion = true;
  sensors.distanceCm = 50;
  runFor(1000);
  assert(lastDuty == 255);
  command("MANUAL 80\n");
  connected = false;
  sensors.pirMotion = false;
  runFor(2200);
  assert(lastDuty == 64 && Serial.output.find("mqtt=0") != std::string::npos);
  sensors.pirMotion = true;
  sensors.distanceValid = false;
  runFor(1000);
  assert(lastDuty == 255); // AUTO still runs offline
  connected = true;
  command("MANUAL 80\n");
  ++losses; // Disconnected and reconnected completely between two loop polls.
  sensors.pirMotion = false;
  runFor(2000);
  assert(lastDuty == 64);
  // Actual FirmwareApp -> processor -> controller -> result path, no direct network ACK.
  using namespace MqttProtocol;
  RemoteCommand remote;
  std::strcpy(remote.commandId, "4113a6c8-27a4-4b2d-a37c-2a7956d673aa");
  std::strcpy(remote.bootId, mqttBootId());
  remote.valid = true;
  remote.manual = true;
  remote.brightness = 80;
  remote.session = losses;
  remote.deadlineMs = appNow + 5000;
  const uint32_t appliedAt = appNow;
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::None);
  assert(latestSnapshot.control.mode == ControlMode::Manual && latestSnapshot.control.brightnessTarget == 80);
  assert(latestSnapshot.control.brightnessApplied != 80); // ACK means accepted target, not dimming done
  runFor(2000);
  assert(lastDuty == 204);
  runFor(4000); // deadline now expired; exact retry must still ACK old result
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::None);
  remote.brightness = 79;
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::InvalidCommand && latestSnapshot.control.brightnessTarget == 80);
  runFor(60001 - (appNow - appliedAt));
  assert(latestSnapshot.control.mode == ControlMode::Auto); // duplicate did not refresh 60s
  remote.commandId[35] = 'b';
  remote.brightness = 90;
  remote.deadlineMs = appNow - 1;
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::Expired && latestSnapshot.control.mode == ControlMode::Auto);
  remote.commandId[35] = 'c';
  remote.deadlineMs = appNow + 5000;
  std::strcpy(remote.bootId, "00000000");
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::BootMismatch);
  std::strcpy(remote.bootId, mqttBootId());
  remote.commandId[35] = 'd';
  remote.manual = false;
  remote.brightness = 0;
  // Serial is processed first, then MQTT AUTO wins in the same control loop.
  Serial.input = "MANUAL 40\n";
  enqueueRemote(remote);
  loopFirmware();
  assert(popResult().reason == CommandReason::None && latestSnapshot.control.mode == ControlMode::Auto);
  remote.commandId[35] = 'e';
  remote.manual = true;
  remote.brightness = 100;
  remote.session = losses - 1;
  enqueueRemote(remote);
  loopFirmware();
  CommandResult absent;
  assert(!appMailbox.peekResult(absent) && latestSnapshot.control.mode == ControlMode::Auto);
  std::puts(
    "PASS remote app: ACK after target acceptance, dimming separate, expired/boot/session rejection, duplicate no MANUAL refresh, Serial/MQTT ordering");
  assert(Serial.output.find("P3/A3 lighting control") != std::string::npos);
  std::puts("PASS app integration: one PWM owner/no diagnostic cycle, nonblocking Serial/overflow/parser, manual/AUTO/offline control, sensor/CONTROL logs");
}
