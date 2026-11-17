#include "MqttProtocol.h"

#include <ArduinoJson.h>
#include <cmath>
#include <cstring>

namespace MqttProtocol {
namespace {
struct PayloadReader {
  const uint8_t *data;
  size_t length;
  size_t position = 0;
  int read() {
    return position < length ? data[position++] : -1;
  }
  size_t readBytes(char *buffer, size_t count) {
    size_t copied = 0;
    while (copied < count && position < length) {
      buffer[copied++] = static_cast<char>(data[position++]);
    }
    return copied;
  }
};

bool hexCharacter(char value) {
  return (value >= '0' && value <= '9') || (value >= 'a' && value <= 'f') || (value >= 'A' && value <= 'F');
}

bool validUuid(const char *value) {
  if (!value || std::strlen(value) != 36 || value[14] != '4' || !std::strchr("89abAB", value[19])) {
    return false;
  }
  for (size_t i = 0; i < 36; ++i) {
    if (i == 8 || i == 13 || i == 18 || i == 23) {
      if (value[i] != '-') {
        return false;
      }
    } else if (!hexCharacter(value[i])) {
      return false;
    }
  }
  return true;
}

bool validBoot(const char *value) {
  if (!value || std::strlen(value) != 8) {
    return false;
  }
  for (size_t i = 0; i < 8; ++i) {
    if (!hexCharacter(value[i])) {
      return false;
    }
  }
  return true;
}

void copyLower(char *destination, const char *source) {
  do {
    const char ch = *source++;
    *destination++ = ch >= 'A' && ch <= 'Z' ? ch + ('a' - 'A') : ch;
  } while (source[-1]);
}

size_t encode(JsonDocument &document, const char *topic, char *output, size_t capacity) {
  const size_t length = measureJson(document);
  // Worst-case fixed header + topic length prefix, shared PubSubClient buffer.
  if (document.overflowed() || length >= capacity || length + std::strlen(topic) + 7 > PACKET_CAPACITY) {
    return 0;
  }
  return serializeJson(document, output, capacity) == length ? length : 0;
}

void base(JsonDocument &doc, const char *bootId) {
  doc["schema_version"] = 1;
  doc["node_id"] = NODE_ID;
  doc["boot_id"] = bootId;
}
} // namespace

bool parseCommand(const char *topic, const uint8_t *payload, size_t length, RemoteCommand &command) {
  command = RemoteCommand{};
  if (std::strcmp(topic, COMMAND_TOPIC) != 0 || length == 0 || length + std::strlen(topic) + 7 > PACKET_CAPACITY) {
    return false;
  }
  // Reject embedded NUL/trailing garbage rather than accepting a valid prefix.
  if (std::memchr(payload, 0, length)) {
    return false;
  }
  JsonDocument doc;
  PayloadReader reader{payload, length};
  if (deserializeJson(doc, reader, DeserializationOption::NestingLimit(4)) || !doc.is<JsonObject>()) {
    return false;
  }
  while (reader.position < length) {
    const int ch = reader.read();
    if (ch != ' ' && ch != '\r' && ch != '\n' && ch != '\t') {
      return false;
    }
  }
  const char *id = doc["command_id"].as<const char *>();
  if (!validUuid(id) || doc["command_id"].as<JsonString>().size() != 36) {
    return false;
  }
  copyLower(command.commandId, id);
  const char *node = doc["node_id"].as<const char *>();
  const char *boot = doc["boot_id"].as<const char *>();
  const char *mode = doc["mode"].as<const char *>();
  bool valid = node && std::strcmp(node, NODE_ID) == 0 && doc["node_id"].as<JsonString>().size() == std::strlen(NODE_ID) && validBoot(boot) &&
               doc["boot_id"].as<JsonString>().size() == 8 && doc["schema_version"].is<unsigned int>() && doc["schema_version"].as<unsigned int>() == 1 &&
               doc["deadline_uptime_ms"].is<uint64_t>();
  if (validBoot(boot)) {
    copyLower(command.bootId, boot);
  }
  command.deadlineMs = doc["deadline_uptime_ms"].as<uint64_t>();
  if (mode && std::strcmp(mode, "MANUAL") == 0 && doc["mode"].as<JsonString>().size() == 6) {
    command.manual = true;
    valid = valid && doc["brightness"].is<unsigned int>() && doc["brightness"].as<unsigned int>() <= 100;
    command.brightness = doc["brightness"].as<uint8_t>();
  } else {
    valid = valid && mode && std::strcmp(mode, "AUTO") == 0 && doc["mode"].as<JsonString>().size() == 4 && doc["brightness"].isUnbound();
  }
  for (JsonPair field : doc.as<JsonObject>()) {
    const char *key = field.key().c_str();
    if (field.key().size() != std::strlen(key)) {
      valid = false;
    }
    if (std::strcmp(key, "schema_version") && std::strcmp(key, "node_id") && std::strcmp(key, "boot_id") && std::strcmp(key, "command_id") &&
        std::strcmp(key, "deadline_uptime_ms") && std::strcmp(key, "mode") && std::strcmp(key, "brightness")) {
      valid = false;
    }
  }
  command.valid = valid;
  return true;
}

size_t encodeTelemetry(const TelemetrySnapshot &snapshot, const char *bootId, uint64_t seq, char *output, size_t capacity) {
  const auto &sensors = snapshot.sensors;
  const auto &control = snapshot.control;
  if (sensors.ldrAdc > 4095 || sensors.currentAdc > 4095 || control.brightnessTarget > 100 || control.brightnessApplied > 100) {
    return 0;
  }
  JsonDocument doc;
  base(doc, bootId);
  doc["seq"] = seq;
  doc["uptime_ms"] = snapshot.uptimeMs;
  doc["mode"] = controlModeName(control.mode);
  doc["environment"] = environmentName(control.environment);
  doc["motion"] = motionName(control.motion);
  doc["ldr_adc"] = sensors.ldrAdc;
  doc["current_adc"] = sensors.currentAdc;
  if (sensors.distanceValid && std::isfinite(sensors.distanceCm) && sensors.distanceCm > 0) {
    doc["distance_cm"] = sensors.distanceCm;
  } else {
    doc["distance_cm"] = nullptr;
  }
  doc["brightness_target"] = control.brightnessTarget;
  doc["brightness_applied"] = control.brightnessApplied;
  const double currentMa = 2000.0 * control.brightnessApplied / 100.0 * sensors.currentAdc / 4095.0;
  doc["current_ma_sim"] = currentMa;
  doc["power_sim_w"] = 12.0 * currentMa / 1000.0;
  JsonArray faults = doc["faults"].to<JsonArray>();
  if (control.openLoad) {
    faults.add("OPEN_LOAD");
  }
  return encode(doc, TELEMETRY_TOPIC, output, capacity);
}

size_t encodeResult(const CommandResult &result, const char *bootId, char *output, size_t capacity) {
  JsonDocument doc;
  base(doc, bootId);
  doc["command_id"] = result.commandId;
  doc["result"] = result.reason == CommandReason::None ? "APPLIED" : "REJECTED";
  switch (result.reason) {
    case CommandReason::None:
      doc["reason"] = nullptr;
      break;
    case CommandReason::BootMismatch:
      doc["reason"] = "BOOT_MISMATCH";
      break;
    case CommandReason::Expired:
      doc["reason"] = "EXPIRED";
      break;
    default:
      doc["reason"] = "INVALID_COMMAND";
      break;
  }
  return encode(doc, ACK_TOPIC, output, capacity);
}

size_t encodeAvailability(const char *bootId, bool online, char *output, size_t capacity) {
  JsonDocument doc;
  base(doc, bootId);
  doc["status"] = online ? "ONLINE" : "OFFLINE";
  return encode(doc, AVAILABILITY_TOPIC, output, capacity);
}

bool controlChanged(const ControlState &left, const ControlState &right) {
  return left.mode != right.mode || left.environment != right.environment || left.motion != right.motion || left.brightnessTarget != right.brightnessTarget ||
         left.brightnessApplied != right.brightnessApplied || left.openLoad != right.openLoad;
}

bool sensorsChanged(const SensorSnapshot &left, const SensorSnapshot &right) {
  // Compare published fields only. Sampling counters and invalid distances (wire null) are not new data.
  const bool leftDistanceValid = left.distanceValid && std::isfinite(left.distanceCm) && left.distanceCm > 0;
  const bool rightDistanceValid = right.distanceValid && std::isfinite(right.distanceCm) && right.distanceCm > 0;
  return left.ldrAdc != right.ldrAdc || left.currentAdc != right.currentAdc || left.pirMotion != right.pirMotion || leftDistanceValid != rightDistanceValid ||
         (leftDistanceValid && left.distanceCm != right.distanceCm);
}

void CommandProcessor::reset(const char *bootId) {
  std::strcpy(currentBootId, bootId);
  count = 0;
  next = 0;
}

CommandResult CommandProcessor::evaluate(const RemoteCommand &command, uint64_t nowMs, bool &apply) {
  apply = false;
  CommandResult result;
  std::strcpy(result.commandId, command.commandId);
  result.session = command.session;
  if (command.valid && std::strcmp(command.bootId, currentBootId)) {
    result.reason = CommandReason::BootMismatch;
    return result;
  }
  for (size_t i = 0; i < count; ++i) {
    const auto &entry = entries[i];
    if (std::strcmp(entry.command.commandId, command.commandId) == 0) {
      const auto &old = entry.command;
      const bool same =
        old.valid == command.valid && old.manual == command.manual && old.brightness == command.brightness && old.deadlineMs == command.deadlineMs;
      result.reason = same ? entry.reason : CommandReason::InvalidCommand;
      return result;
    }
  }
  result.reason = !command.valid ? CommandReason::InvalidCommand : (nowMs > command.deadlineMs ? CommandReason::Expired : CommandReason::None);
  apply = result.reason == CommandReason::None;
  entries[next] = {command, result.reason};
  next = (next + 1) % 32;
  if (count < 32) {
    ++count;
  }
  return result;
}
} // namespace MqttProtocol
