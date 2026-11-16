#pragma once

#include <stdint.h>
#include "MqttProtocol.h"

// PubSubClient is owned by its task; control code only reads an atomic status.
bool startConnectivity();
bool isMqttConnected();
uint32_t mqttDisconnectCount();
const char *mqttBootId();
uint64_t firmwareUptimeMs();
void updateMqttSnapshot(const MqttProtocol::TelemetrySnapshot &snapshot);
bool takeRemoteCommand(MqttProtocol::RemoteCommand &command);
bool completeRemoteCommand(const MqttProtocol::CommandResult &result);
