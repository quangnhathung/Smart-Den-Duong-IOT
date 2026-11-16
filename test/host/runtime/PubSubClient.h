#pragma once

#include "WiFi.h"
#include <cstring>
#include <string>
#include <vector>

struct FakePacket {
  std::string topic;
  std::string payload;
  bool retained;
};
struct PubSubClient {
  bool connectedValue = false;
  bool connectSucceeds = true;
  bool subscribeSucceeds = true;
  bool loopSucceeds = true;
  unsigned int connects = 0;
  unsigned int subscribes = 0;
  unsigned int loops = 0;
  uint8_t subscribedQos = 0;
  std::string subscribedTopic;
  std::vector<FakePacket> packets;
  void (*callback)(char *, uint8_t *, unsigned int) = nullptr;
  explicit PubSubClient(WiFiClient &) {}
  void setServer(const char *, uint16_t) {}
  void setSocketTimeout(uint16_t) {}
  void setKeepAlive(uint16_t) {}
  void setCallback(void (*handler)(char *, uint8_t *, unsigned int)) {
    callback = handler;
  }
  bool setBufferSize(uint16_t) {
    return true;
  }
  bool connected() {
    return connectedValue;
  }
  int state() {
    return connectedValue ? 0 : -2;
  }
  bool connect(const char *) {
    ++connects;
    connectedValue = connectSucceeds;
    return connectedValue;
  }
  bool subscribe(const char *topic, uint8_t qos) {
    ++subscribes;
    subscribedTopic = topic;
    subscribedQos = qos;
    return subscribeSucceeds;
  }
  void disconnect() {
    connectedValue = false;
  }
  bool loop() {
    ++loops;
    if (!loopSucceeds) {
      connectedValue = false;
    }
    return loopSucceeds;
  }
  bool publish(const char *topic, const uint8_t *payload, unsigned int length, bool retained) {
    packets.push_back({topic, std::string(reinterpret_cast<const char *>(payload), length), retained});
    return connectedValue;
  }
  bool publish(const char *topic, const char *payload, bool retained) {
    return publish(topic, reinterpret_cast<const uint8_t *>(payload), static_cast<unsigned int>(std::strlen(payload)), retained);
  }
};
