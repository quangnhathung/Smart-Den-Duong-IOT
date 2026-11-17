#include "Connectivity.h"
#include "MqttMailbox.h"

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <algorithm>
#include <atomic>
#include <esp_random.h>
#include <esp_timer.h>

namespace {
using NodeIdentity::HEARTBEAT_TOPIC;
using NodeIdentity::PING_TOPIC;
using NodeIdentity::PONG_TOPIC;
std::atomic<bool> mqttConnected{false};
std::atomic<uint32_t> disconnectCount{0};
WiFiClient networkClient;
PubSubClient mqtt(networkClient);
uint32_t lastAttemptMs = 0;
uint32_t lastHeartbeatMs = 0;
uint32_t retryMs = 1000;
bool wasConnected = false;
bool mqttReady = false;
char bootId[9] = {};
char willPayload[192] = {};
char packetBuffer[MqttProtocol::PACKET_CAPACITY];
MqttMailbox mailbox;
portMUX_TYPE mailboxMux = portMUX_INITIALIZER_UNLOCKED;
uint64_t telemetrySeq = 0;
uint64_t lastTelemetryGeneration = 0;
uint64_t lastTelemetrySentMs = 0;
uint64_t lastTelemetryAttemptMs = 0;
bool haveTelemetryAttempt = false;
bool forceTelemetry = true;
bool onlinePending = true;

bool publishPacket(const char *topic, size_t length, bool retained) {
  return length && mqtt.publish(topic, reinterpret_cast<const uint8_t *>(packetBuffer), length, retained);
}

void closeSession() {
  mqttConnected.store(false);
  portENTER_CRITICAL(&mailboxMux);
  mailbox.disconnect();
  portEXIT_CRITICAL(&mailboxMux);
  // If a clean DISCONNECT can be sent, publish OFFLINE first; otherwise leave the will armed.
  if (WiFi.status() == WL_CONNECTED && mqtt.connected()) {
    const size_t length = MqttProtocol::encodeAvailability(bootId, false, packetBuffer, sizeof(packetBuffer));
    if (publishPacket(MqttProtocol::AVAILABILITY_TOPIC, length, true)) {
      mqtt.disconnect();
      return;
    }
  }
  networkClient.stop();
}

void publishBusiness() {
  using namespace MqttProtocol;
  if (onlinePending) {
    const size_t length = encodeAvailability(bootId, true, packetBuffer, sizeof(packetBuffer));
    if (!publishPacket(AVAILABILITY_TOPIC, length, true)) {
      return;
    }
    onlinePending = false;
  }
  CommandResult result;
  portENTER_CRITICAL(&mailboxMux);
  const bool haveResult = mailbox.peekResult(result);
  portEXIT_CRITICAL(&mailboxMux);
  if (haveResult) {
    const bool stale = result.session != disconnectCount.load();
    const size_t length = stale ? 0 : encodeResult(result, bootId, packetBuffer, sizeof(packetBuffer));
    if (stale || publishPacket(ACK_TOPIC, length, false)) {
      portENTER_CRITICAL(&mailboxMux);
      mailbox.popResult();
      portEXIT_CRITICAL(&mailboxMux);
    }
  }
  TelemetrySnapshot snapshot;
  uint64_t generation;
  portENTER_CRITICAL(&mailboxMux);
  const bool ready = mailbox.latest(snapshot, generation);
  portEXIT_CRITICAL(&mailboxMux);
  const uint64_t nowMs = firmwareUptimeMs();
  if (!ready || (haveTelemetryAttempt && nowMs - lastTelemetryAttemptMs < 200) ||
      (!forceTelemetry && generation == lastTelemetryGeneration && nowMs - lastTelemetrySentMs < 2000)) {
    return;
  }
  lastTelemetryAttemptMs = nowMs;
  haveTelemetryAttempt = true;
  const size_t length = encodeTelemetry(snapshot, bootId, telemetrySeq, packetBuffer, sizeof(packetBuffer));
  if (publishPacket(TELEMETRY_TOPIC, length, false)) {
    ++telemetrySeq;
    lastTelemetryGeneration = generation;
    lastTelemetrySentMs = nowMs;
    forceTelemetry = false;
  } else {
    Serial.println("MQTT telemetry serialize/publish failed");
  }
}

void receivePing(char *topic, uint8_t *payload, unsigned int length) {
  if (strcmp(topic, MqttProtocol::COMMAND_TOPIC) == 0) {
    MqttProtocol::RemoteCommand command;
    if (!mqttConnected.load() || !MqttProtocol::parseCommand(topic, payload, length, command)) {
      Serial.println("MQTT command dropped: malformed payload, ID or session");
      return;
    }
    command.session = disconnectCount.load();
    portENTER_CRITICAL(&mailboxMux);
    const bool queued = mailbox.enqueue(command);
    portEXIT_CRITICAL(&mailboxMux);
    if (!queued) {
      Serial.println("MQTT command queue full; not applied");
    }
    return;
  }
  if (strcmp(topic, PING_TOPIC) != 0 || length > 64) {
    Serial.println("PING rejected: topic or length");
    return;
  }
  uint8_t copy[64];
  memcpy(copy, payload, length);
  const bool sent = mqtt.publish(PONG_TOPIC, copy, length, false);
  Serial.printf("PING bytes=%u PONG published=%d\r\n", length, sent);
}

void publishHeartbeat(uint32_t nowMs) {
  if (nowMs - lastHeartbeatMs < 2000U) {
    return;
  }
  lastHeartbeatMs = nowMs;
  char payload[48];
  const int length = snprintf(payload, sizeof(payload), "{\"uptime_ms\":%lu}", static_cast<unsigned long>(nowMs));
  const bool sent = length > 0 && static_cast<size_t>(length) < sizeof(payload) && mqtt.publish(HEARTBEAT_TOPIC, payload, false);
  Serial.printf("uptime_ms=%lu HEARTBEAT published=%d state=%d\r\n", static_cast<unsigned long>(nowMs), sent, mqtt.state());
}

void networkStep() {
  const uint32_t nowMs = millis();
  bool connected = WiFi.status() == WL_CONNECTED && mqtt.connected();
  if (connected && wasConnected) {
    retryMs = 1000;
    if (mqtt.loop()) {
      publishHeartbeat(millis());
      publishBusiness();
    } else {
      Serial.printf("uptime_ms=%lu MQTT loop failed state=%d\r\n", static_cast<unsigned long>(millis()), mqtt.state());
    }
    connected = WiFi.status() == WL_CONNECTED && mqtt.connected();
  }
  if (!connected) {
    mqttConnected.store(false);
    if (wasConnected) {
      Serial.printf("uptime_ms=%lu MQTT disconnected state=%d wifi=%d\r\n", static_cast<unsigned long>(millis()), mqtt.state(), WiFi.status());
      wasConnected = false;
      disconnectCount.fetch_add(1);
      closeSession(); // Keep will armed when transport is already lost.
      return;         // Publish loss before attempting a new session on a later network tick.
    }
    if (nowMs - lastAttemptMs < retryMs) {
      return;
    }
    lastAttemptMs = nowMs;
    if (WiFi.status() != WL_CONNECTED) {
      const bool started = WiFi.reconnect();
      Serial.printf("uptime_ms=%lu WiFi reconnect started=%d wifi=%d\r\n", static_cast<unsigned long>(millis()), started, WiFi.status());
    } else if (mqttReady) {
      Serial.printf("uptime_ms=%lu MQTT connect attempt retry_ms=%lu\r\n", static_cast<unsigned long>(nowMs), static_cast<unsigned long>(retryMs));
      if (mqtt.connect(NodeIdentity::CLIENT_ID, nullptr, nullptr, MqttProtocol::AVAILABILITY_TOPIC, 0, true, willPayload, true) &&
          mqtt.subscribe(PING_TOPIC, 1) && mqtt.subscribe(MqttProtocol::COMMAND_TOPIC, 1)) {
        wasConnected = true;
        mqttConnected.store(true);
        lastHeartbeatMs = millis();
        onlinePending = true;
        forceTelemetry = true;
        retryMs = 1000;
        Serial.println("MQTT connected; ping subscribed");
        return;
      }
      Serial.printf("uptime_ms=%lu MQTT connect failed state=%d wifi=%d\r\n", static_cast<unsigned long>(millis()), mqtt.state(), WiFi.status());
      closeSession();
    }
    retryMs = std::min<uint32_t>(retryMs * 2U, 10000U);
  } else {
    mqttConnected.store(true);
  }
}

void networkTask(void *) {
  networkClient.setConnectionTimeout(1000);
  mqtt.setServer("host.wokwi.internal", 1883);
  mqtt.setSocketTimeout(1);
  mqtt.setKeepAlive(15);
  mqtt.setCallback(receivePing);
  mqttReady = mqtt.setBufferSize(2048);
  if (!mqttReady) {
    Serial.println("MQTT buffer allocation failed; AUTO remains active");
  }
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(false);
  WiFi.begin("Wokwi-GUEST", "", 6);
  for (;;) {
    networkStep();
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
} // namespace

bool startConnectivity() {
  snprintf(bootId, sizeof(bootId), "%08lx", static_cast<unsigned long>(esp_random()));
  if (!MqttProtocol::encodeAvailability(bootId, false, willPayload, sizeof(willPayload))) {
    Serial.println("MQTT will serialization failed");
    return false;
  }
  return xTaskCreatePinnedToCore(networkTask, "smartlight-mqtt", 8192, nullptr, 1, nullptr, 0) == pdPASS;
}

bool isMqttConnected() {
  return mqttConnected.load();
}

uint32_t mqttDisconnectCount() {
  return disconnectCount.load();
}

const char *mqttBootId() {
  return bootId;
}

uint64_t firmwareUptimeMs() {
  return static_cast<uint64_t>(esp_timer_get_time()) / 1000;
}

void updateMqttSnapshot(const MqttProtocol::TelemetrySnapshot &snapshot) {
  portENTER_CRITICAL(&mailboxMux);
  mailbox.update(snapshot);
  portEXIT_CRITICAL(&mailboxMux);
}

bool takeRemoteCommand(MqttProtocol::RemoteCommand &command) {
  portENTER_CRITICAL(&mailboxMux);
  const bool taken = mailbox.takeCommand(command);
  portEXIT_CRITICAL(&mailboxMux);
  return taken;
}

bool completeRemoteCommand(const MqttProtocol::CommandResult &result) {
  portENTER_CRITICAL(&mailboxMux);
  const bool queued = result.session == disconnectCount.load() && mqttConnected.load() && mailbox.complete(result);
  portEXIT_CRITICAL(&mailboxMux);
  return queued;
}
