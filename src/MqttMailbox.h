#pragma once

#include "MqttProtocol.h"

// Access only while holding Connectivity's short critical section; no network/JSON inside it.
class MqttMailbox {
public:
  static constexpr size_t CAPACITY = 8;

  bool enqueue(const MqttProtocol::RemoteCommand &command) {
    if (commandCount == CAPACITY) {
      return false;
    }
    commands[(commandHead + commandCount++) % CAPACITY] = command;
    return true;
  }

  bool takeCommand(MqttProtocol::RemoteCommand &command) {
    // Only the control core produces results; one in-flight command reserves this free slot.
    if (!commandCount || resultCount == CAPACITY) {
      return false;
    }
    command = commands[commandHead];
    commandHead = (commandHead + 1) % CAPACITY;
    --commandCount;
    return true;
  }

  bool complete(const MqttProtocol::CommandResult &result) {
    if (resultCount == CAPACITY) {
      return false;
    }
    results[(resultHead + resultCount++) % CAPACITY] = result;
    return true;
  }

  bool peekResult(MqttProtocol::CommandResult &result) const {
    if (!resultCount) {
      return false;
    }
    result = results[resultHead];
    return true;
  }

  void popResult() {
    if (resultCount) {
      resultHead = (resultHead + 1) % CAPACITY;
      --resultCount;
    }
  }

  void disconnect() {
    commandHead = commandCount = resultHead = resultCount = 0;
  }

  void update(const MqttProtocol::TelemetrySnapshot &value) {
    if (!ready || MqttProtocol::controlChanged(snapshot.control, value.control) || MqttProtocol::sensorsChanged(snapshot.sensors, value.sensors)) {
      ++generation;
    }
    snapshot = value;
    ready = true;
  }

  bool latest(MqttProtocol::TelemetrySnapshot &value, uint64_t &version) const {
    value = snapshot;
    version = generation;
    return ready;
  }

private:
  MqttProtocol::RemoteCommand commands[CAPACITY];
  MqttProtocol::CommandResult results[CAPACITY];
  size_t commandHead = 0;
  size_t commandCount = 0;
  size_t resultHead = 0;
  size_t resultCount = 0;
  MqttProtocol::TelemetrySnapshot snapshot;
  uint64_t generation = 0;
  bool ready = false;
};
