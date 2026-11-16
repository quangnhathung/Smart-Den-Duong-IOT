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
  WiFiClient &client;
  bool connectedValue = false;
  bool publishSucceeds = true;
  std::string willTopic;
  std::string willPayload;
  bool willRetain = false;
  bool cleanSession = false;
  uint8_t willQos = 99;
  std::vector<std::string> subscriptions;
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
  explicit PubSubClient(WiFiClient &value) : client(value) {}
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
    return connectedValue && client.open;
  }
  int state() {
    return connectedValue ? 0 : -2;
  }
  bool connect(const char *) {
    ++connects;
    connectedValue = connectSucceeds;
    client.open = connectSucceeds;
    return connectedValue && client.open;
  }
  bool connect(const char *id, const char *, const char *, const char *topic, uint8_t qos, bool retained, const char *payload, bool clean) {
    willTopic = topic;
    willPayload = payload;
    willQos = qos;
    willRetain = retained;
    cleanSession = clean;
    return connect(id);
  }
  bool subscribe(const char *topic, uint8_t qos) {
    ++subscribes;
    subscriptions.emplace_back(topic);
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
    if (!connected() || !publishSucceeds) {
      return false;
    }
    packets.push_back({topic, std::string(reinterpret_cast<const char *>(payload), length), retained});
    return connectedValue && client.open;
  }
  bool publish(const char *topic, const char *payload, bool retained) {
    return publish(topic, reinterpret_cast<const uint8_t *>(payload), static_cast<unsigned int>(std::strlen(payload)), retained);
  }
};
