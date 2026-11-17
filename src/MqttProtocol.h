#pragma once

#include "ControlTypes.h"
#include "NodeIdentity.h"
#include "SensorReader.h"
#include <stddef.h>
#include <stdint.h>

namespace MqttProtocol {
using NodeIdentity::ACK_TOPIC;
using NodeIdentity::AVAILABILITY_TOPIC;
using NodeIdentity::COMMAND_TOPIC;
using NodeIdentity::NODE_ID;
using NodeIdentity::TELEMETRY_TOPIC;
constexpr size_t PACKET_CAPACITY = 2048;

enum class CommandReason { None, InvalidCommand, BootMismatch, Expired };

struct RemoteCommand {
  char commandId[37] = {};
  char bootId[9] = {};
  uint64_t deadlineMs = 0;
  uint32_t session = 0;
  bool valid = false;
  bool manual = false;
  uint8_t brightness = 0;
};

struct CommandResult {
  char commandId[37] = {};
  uint32_t session = 0;
  CommandReason reason = CommandReason::InvalidCommand;
};

struct TelemetrySnapshot {
  SensorSnapshot sensors = {};
  ControlState control;
  uint64_t uptimeMs = 0;
};

// false means no trustworthy command ID, malformed JSON, or wrong destination: log/drop only.
bool parseCommand(const char *topic, const uint8_t *payload, size_t length, RemoteCommand &command);
size_t encodeTelemetry(const TelemetrySnapshot &snapshot, const char *bootId, uint64_t seq, char *output, size_t capacity);
size_t encodeResult(const CommandResult &result, const char *bootId, char *output, size_t capacity);
size_t encodeAvailability(const char *bootId, bool online, char *output, size_t capacity);
bool controlChanged(const ControlState &left, const ControlState &right);
bool sensorsChanged(const SensorSnapshot &left, const SensorSnapshot &right);

class CommandProcessor {
public:
  void reset(const char *bootId);
  // Call only on the control core; apply only when apply=true, then enqueue result.
  CommandResult evaluate(const RemoteCommand &command, uint64_t nowMs, bool &apply);

private:
  struct Entry {
    RemoteCommand command;
    CommandReason reason = CommandReason::InvalidCommand;
  };
  Entry entries[32];
  size_t count = 0;
  size_t next = 0;
  char currentBootId[9] = {};
};
} // namespace MqttProtocol
