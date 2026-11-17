#include "FirmwareApp.h"
#include "Connectivity.h"
#include "LightingController.h"
#include "LocalControlCommand.h"
#include "SensorReader.h"

#include <Arduino.h>
#include <esp_arduino_version.h>

namespace {
constexpr uint8_t LED_PIN = 26;
LightingController controller;
MqttProtocol::CommandProcessor commandProcessor;
bool pwmReady = false;
int lastDuty = -1;
bool lastPirMotion = false;
uint32_t lastLogMs = 0;
uint32_t lastDisconnectCount = 0;
char commandBuffer[32];
uint8_t commandLength = 0;
bool commandOverflow = false;

void readLocalCommands(uint32_t nowMs) {
  // Bound work even if the terminal is flooded. Discard the whole malformed line.
  for (uint8_t count = 0; count < 16 && Serial.available() > 0; ++count) {
    const int value = Serial.read();
    if (value == '\r') {
      continue;
    }
    if (value == '\n') {
      commandBuffer[commandLength] = '\0';
      LocalControlCommand command;
      bool accepted = !commandOverflow && parseLocalControlCommand(commandBuffer, command);
      if (accepted) {
        if (command.manual) {
          // MANUAL immediately falls back if disconnected, just as the controller requires.
          accepted = isMqttConnected() && controller.requestManual(command.brightness, nowMs);
        } else {
          controller.requestAuto();
        }
      }
      Serial.printf("LOCAL command accepted=%d; use AUTO or MANUAL 0..100 (MQTT connected)\r\n", accepted);
      commandLength = 0;
      commandOverflow = false;
    } else if (commandLength < sizeof(commandBuffer) - 1) {
      if (value < 32 || value > 126) {
        commandOverflow = true;
      } else {
        commandBuffer[commandLength++] = static_cast<char>(value);
      }
    } else {
      commandOverflow = true;
    }
  }
}

void writePwm(const ControlState &state) {
  const uint8_t duty = brightnessToDuty(state.brightnessApplied);
  if (pwmReady && duty != lastDuty) {
    if (ledcWrite(LED_PIN, duty)) {
      lastDuty = duty;
    } else {
      Serial.println("PWM write failed");
    }
  }
}

void logState(uint32_t nowMs, const ControlState &state) {
  const SensorSnapshot &sensors = getSensorSnapshot();
  Serial.printf("CONTROL uptime_ms=%lu mode=%s environment=%s motion=%s ldr_filtered=%u target=%u applied=%u duty=%u ready=%d fault=%s mqtt=%d\r\n",
                static_cast<unsigned long>(nowMs), controlModeName(state.mode), environmentName(state.environment), motionName(state.motion),
                static_cast<unsigned int>(state.filteredLdrAdc), state.brightnessTarget, state.brightnessApplied, brightnessToDuty(state.brightnessApplied),
                pwmReady, state.openLoad ? "OPEN_LOAD" : "OK", isMqttConnected());
  // One printf per line to keep network-task Serial messages from splitting sensor lines.
  if (sensors.distanceValid) {
    Serial.printf("SENSORS uptime_ms=%lu ldr_adc=%u pir=%d current_adc=%u distance_valid=1 distance_cm=%.2f\r\n", static_cast<unsigned long>(nowMs),
                  sensors.ldrAdc, sensors.pirMotion, sensors.currentAdc, static_cast<double>(sensors.distanceCm));
  } else {
    Serial.printf("SENSORS uptime_ms=%lu ldr_adc=%u pir=%d current_adc=%u distance_valid=0 distance_cm=NA\r\n", static_cast<unsigned long>(nowMs),
                  sensors.ldrAdc, sensors.pirMotion, sensors.currentAdc);
  }
}
} // namespace

void setupFirmware() {
  Serial.begin(115200);
  Serial.printf("P3/A3 lighting control %s Arduino=%s; Serial: AUTO / MANUAL 0..100\r\n", MqttProtocol::NODE_ID, ESP_ARDUINO_VERSION_STR);
  setupSensors();
  controller.reset(millis());
  lastPirMotion = getSensorSnapshot().pirMotion;
  pwmReady = ledcAttach(LED_PIN, 5000, 8);
  if (!pwmReady) {
    Serial.println("PWM attach failed");
  }
  writePwm(controller.state());
  if (!startConnectivity()) {
    Serial.println("MQTT task creation failed; AUTO continues offline");
  }
  commandProcessor.reset(mqttBootId());
}

void loopFirmware() {
  const uint32_t nowMs = millis();
  updateSensors(nowMs);
  readLocalCommands(nowMs);
  const SensorSnapshot &sensors = getSensorSnapshot();
  ControlInput input;
  input.ldrAdc = sensors.ldrAdc;
  input.currentAdc = sensors.currentAdc;
  input.pirMotion = sensors.pirMotion;
  input.distanceValid = sensors.distanceValid;
  input.distanceCm = sensors.distanceCm;
  input.analogSequence = sensors.analogSequence;
  const uint32_t disconnectCount = mqttDisconnectCount();
  // A quick disconnect/reconnect must still cancel MANUAL, even between control polls.
  const bool connectedForControl = isMqttConnected() && disconnectCount == lastDisconnectCount;
  lastDisconnectCount = disconnectCount;
  MqttProtocol::RemoteCommand command;
  MqttProtocol::CommandResult result;
  bool haveResult = false;
  if (takeRemoteCommand(command) && connectedForControl && command.session == disconnectCount) {
    bool apply = false;
    result = commandProcessor.evaluate(command, firmwareUptimeMs(), apply);
    if (apply) {
      if (command.manual) {
        controller.requestManual(command.brightness, nowMs);
      } else {
        controller.requestAuto();
      }
    }
    haveResult = true;
  }
  const ControlState &state = controller.update(input, nowMs, connectedForControl);
  if (haveResult && !completeRemoteCommand(result)) {
    Serial.println("MQTT result discarded after session loss");
  }
  MqttProtocol::TelemetrySnapshot snapshot;
  snapshot.sensors = sensors;
  snapshot.control = state;
  snapshot.uptimeMs = firmwareUptimeMs();
  updateMqttSnapshot(snapshot);
  writePwm(state);
  if (sensors.pirMotion != lastPirMotion) {
    Serial.printf("PIR uptime_ms=%lu motion=%d\r\n", static_cast<unsigned long>(nowMs), sensors.pirMotion);
    lastPirMotion = sensors.pirMotion;
  }
  if (nowMs - lastLogMs >= 1000U) {
    lastLogMs = nowMs;
    logState(nowMs, state);
  }
  delay(1); // Yield one tick; no sensor/network wait in the control loop.
}
