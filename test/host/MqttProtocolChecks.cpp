#include "MqttMailbox.h"
#include "MqttProtocol.h"
#include <ArduinoJson.h>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <string>

using namespace MqttProtocol;
namespace {
std::string commandJson(unsigned int number = 1) {
  char id[37];
  std::snprintf(id, sizeof(id), "4113a6c8-27a4-4b2d-a37c-%012u", number);
  JsonDocument doc;
  doc["schema_version"] = 1;
  doc["node_id"] = NODE_ID;
  doc["boot_id"] = "b7e28a10";
  doc["command_id"] = id;
  doc["deadline_uptime_ms"] = uint64_t(5000000000ULL);
  doc["mode"] = "MANUAL";
  doc["brightness"] = 80;
  std::string output;
  serializeJson(doc, output);
  return output;
}
RemoteCommand parse(const std::string &json) {
  RemoteCommand command;
  assert(parseCommand(COMMAND_TOPIC, reinterpret_cast<const uint8_t *>(json.data()), json.size(), command));
  return command;
}
std::string stringify(JsonDocument &doc) {
  std::string text;
  serializeJson(doc, text);
  return text;
}
void checkParser() {
  const std::string json = commandJson();
  assert(parse(json).valid && parse(json).manual && parse(json).brightness == 80);
  assert(parse(json + " \r\n").valid);
  for (const std::string &bad : {json + "x", json + "{}", json + " }", std::string("{}"), std::string("[1]"), json.substr(0, 50),
                                 std::string("{\"command_id\":true}"), json + std::string(1, '\0')}) {
    RemoteCommand value;
    assert(!parseCommand(COMMAND_TOPIC, reinterpret_cast<const uint8_t *>(bad.data()), bad.size(), value));
  }
  RemoteCommand value;
  const std::string oversized(2048, ' ');
  assert(!parseCommand(COMMAND_TOPIC, reinterpret_cast<const uint8_t *>(oversized.data()), oversized.size(), value));
  assert(!parseCommand("other", reinterpret_cast<const uint8_t *>(json.data()), json.size(), value));
  for (const char *brightness : {"-1", "101", "1.5", "true", "null", "\"80\""}) {
    std::string bad = json;
    bad.replace(bad.find("\"brightness\":80"), 15, std::string("\"brightness\":") + brightness);
    assert(!parse(bad).valid);
  }
  for (const char *field : {"schema_version", "node_id", "boot_id", "mode", "deadline_uptime_ms", "brightness"}) {
    JsonDocument doc;
    assert(!deserializeJson(doc, json));
    doc.remove(field);
    assert(!parse(stringify(doc)).valid);
  }
  for (const char *field : {"schema_version", "deadline_uptime_ms"}) {
    JsonDocument doc;
    deserializeJson(doc, json);
    doc[field] = true;
    assert(!parse(stringify(doc)).valid);
    doc[field] = -1;
    assert(!parse(stringify(doc)).valid);
    doc[field] = 1.0;
    // JSON serialization can normalize 1.0 to 1; test raw double token separately below.
  }
  std::string floating = json;
  floating.replace(floating.find("\"schema_version\":1"), 18, "\"schema_version\":1.0");
  assert(!parse(floating).valid);
  JsonDocument doc;
  deserializeJson(doc, json);
  doc["mode"] = "AUTO";
  assert(!parse(stringify(doc)).valid);
  doc.remove("brightness");
  assert(parse(stringify(doc)).valid && !parse(stringify(doc)).manual);
  doc["extra"] = 1;
  assert(!parse(stringify(doc)).valid);
  doc.remove("extra");
  doc["node_id"] = "node_02";
  assert(!parse(stringify(doc)).valid);
  std::puts("PASS protocol parser: strict fields/types/ranges, UUID/boot, complete JSON, wrong topic/node, malformed/oversized payload");
}
void checkCache() {
  CommandProcessor processor;
  processor.reset("b7e28a10");
  auto command = parse(commandJson());
  bool apply = false;
  assert(processor.evaluate(command, command.deadlineMs, apply).reason == CommandReason::None && apply);
  assert(processor.evaluate(command, command.deadlineMs + 1, apply).reason == CommandReason::None && !apply);
  command.brightness = 79;
  assert(processor.evaluate(command, 0, apply).reason == CommandReason::InvalidCommand && !apply);
  command.brightness = 80;
  assert(processor.evaluate(command, 0, apply).reason == CommandReason::None && !apply);
  auto expired = parse(commandJson(2));
  assert(processor.evaluate(expired, expired.deadlineMs + 1, apply).reason == CommandReason::Expired && !apply);
  assert(processor.evaluate(expired, 0, apply).reason == CommandReason::Expired && !apply);
  std::strcpy(command.bootId, "00000000");
  assert(processor.evaluate(command, 0, apply).reason == CommandReason::BootMismatch && !apply);
  processor.reset("b7e28a10");
  command = parse(commandJson());
  auto invalid = command;
  invalid.valid = false;
  assert(processor.evaluate(invalid, 0, apply).reason == CommandReason::InvalidCommand && !apply);
  assert(processor.evaluate(command, 0, apply).reason == CommandReason::InvalidCommand && !apply);
  processor.reset("b7e28a10");
  for (unsigned int i = 1; i <= 33; ++i) {
    assert(processor.evaluate(parse(commandJson(i)), 0, apply).reason == CommandReason::None && apply);
  }
  processor.evaluate(parse(commandJson(2)), 0, apply);
  assert(!apply); // cache hit does not evict or refresh FIFO
  processor.evaluate(command, 0, apply);
  assert(apply); // oldest evicted after 33 distinct IDs
  processor.reset("b7e28a10");
  processor.evaluate(command, 0, apply);
  assert(apply);
  std::puts("PASS cache: exact deadline, duplicate after expiry, content conflict, cached rejection, boot mismatch/reset, FIFO32");
}
void checkWire() {
  TelemetrySnapshot snapshot;
  snapshot.sensors.ldrAdc = 3100;
  snapshot.sensors.currentAdc = 4095;
  snapshot.control.brightnessTarget = 80;
  snapshot.control.brightnessApplied = 80;
  snapshot.control.openLoad = true;
  snapshot.uptimeMs = 5000000000ULL;
  char output[2048];
  assert(encodeTelemetry(snapshot, "b7e28a10", 5000000001ULL, output, sizeof(output)));
  JsonDocument doc;
  assert(!deserializeJson(doc, output));
  assert(doc.size() == 16 && doc["schema_version"] == 1 && doc["node_id"] == NODE_ID);
  assert(doc["uptime_ms"].as<uint64_t>() == 5000000000ULL && doc["seq"].as<uint64_t>() == 5000000001ULL);
  assert(doc["distance_cm"].isNull() && doc["faults"][0] == "OPEN_LOAD");
  assert(std::abs(doc["current_ma_sim"].as<double>() - 1600) < 0.01 && std::abs(doc["power_sim_w"].as<double>() - 19.2) < 0.001);
  snapshot.sensors.distanceValid = true;
  for (float distance : {std::numeric_limits<float>::quiet_NaN(), std::numeric_limits<float>::infinity(), 0.0f, -1.0f, 405.5f}) {
    snapshot.sensors.distanceCm = distance;
    assert(encodeTelemetry(snapshot, "b7e28a10", 1, output, sizeof(output)));
    deserializeJson(doc, output);
    assert(doc["distance_cm"].isNull() == !(std::isfinite(distance) && distance > 0));
  }
  assert(!encodeTelemetry(snapshot, "b7e28a10", 1, output, 16));
  snapshot.sensors.currentAdc = 5000;
  assert(!encodeTelemetry(snapshot, "b7e28a10", 1, output, sizeof(output)));
  CommandResult result;
  std::strcpy(result.commandId, parse(commandJson()).commandId);
  for (auto reason : {CommandReason::None, CommandReason::InvalidCommand, CommandReason::BootMismatch, CommandReason::Expired}) {
    result.reason = reason;
    assert(encodeResult(result, "b7e28a10", output, sizeof(output)));
    deserializeJson(doc, output);
    assert(doc.size() == 6 && doc["reason"].isNull() == (reason == CommandReason::None));
    assert(doc["result"] == (reason == CommandReason::None ? "APPLIED" : "REJECTED"));
  }
  assert(encodeAvailability("b7e28a10", false, output, sizeof(output)));
  deserializeJson(doc, output);
  assert(doc.size() == 4 && doc["status"] == "OFFLINE");
  std::puts("PASS wire: full telemetry, uint64 beyond millis wrap, current/power model, null/invalid distance, faults, ACK/availability, bounded buffer");
}
void checkMailbox() {
  MqttMailbox mailbox;
  auto command = parse(commandJson());
  CommandResult result;
  for (size_t i = 0; i < MqttMailbox::CAPACITY; ++i) {
    assert(mailbox.enqueue(command));
  }
  assert(!mailbox.enqueue(command));
  for (size_t i = 0; i < MqttMailbox::CAPACITY; ++i) {
    assert(mailbox.takeCommand(command) && mailbox.complete(result));
  }
  assert(mailbox.enqueue(command) && !mailbox.takeCommand(command));
  assert(!mailbox.complete(result));
  assert(mailbox.peekResult(result));
  mailbox.popResult();
  assert(mailbox.takeCommand(command));
  mailbox.disconnect();
  assert(!mailbox.takeCommand(command) && !mailbox.peekResult(result));
  TelemetrySnapshot snapshot;
  uint64_t version;
  assert(!mailbox.latest(snapshot, version));
  mailbox.update(snapshot);
  assert(mailbox.latest(snapshot, version) && version == 1);
  ++snapshot.sensors.ldrAdc;
  mailbox.update(snapshot);
  assert(mailbox.latest(snapshot, version) && version == 1);
  snapshot.control.openLoad = true;
  mailbox.update(snapshot);
  assert(mailbox.latest(snapshot, version) && version == 2);
  std::puts("PASS mailbox: queue8 overflow, result reservation/backpressure, disconnect flush, coherent latest snapshot/change coalescing");
}
} // namespace
int main() {
  checkParser();
  checkCache();
  checkWire();
  checkMailbox();
}
