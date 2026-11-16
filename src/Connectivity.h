#pragma once

#include <stdint.h>

// PubSubClient is owned by its task; control code only reads an atomic status.
bool startConnectivity();
bool isMqttConnected();
uint32_t mqttDisconnectCount();
