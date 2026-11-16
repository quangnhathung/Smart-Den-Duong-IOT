#include "Connectivity.h"

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <algorithm>
#include <atomic>

namespace {
constexpr char PING_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/ping";
constexpr char PONG_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/pong";
constexpr char HEARTBEAT_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/heartbeat";
std::atomic<bool> mqttConnected{false};
std::atomic<uint32_t> disconnectCount{0};
WiFiClient networkClient;
PubSubClient mqtt(networkClient);
uint32_t lastAttemptMs = 0;
uint32_t lastHeartbeatMs = 0;
uint32_t retryMs = 1000;
bool wasConnected = false;
bool mqttReady = false;

void receivePing(char *topic, uint8_t *payload, unsigned int length) {
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
      mqtt.disconnect(); // Close a stale session after Wi-Fi loss before retry/resubscribe.
      return;            // Publish loss before attempting a new session on a later network tick.
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
      if (mqtt.connect("smartlight-node_01-p0") && mqtt.subscribe(PING_TOPIC, 1)) {
        wasConnected = true;
        mqttConnected.store(true);
        lastHeartbeatMs = millis();
        retryMs = 1000;
        Serial.println("MQTT connected; ping subscribed");
        return;
      }
      Serial.printf("uptime_ms=%lu MQTT connect failed state=%d wifi=%d\r\n", static_cast<unsigned long>(millis()), mqtt.state(), WiFi.status());
      mqtt.disconnect();
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
  return xTaskCreatePinnedToCore(networkTask, "smartlight-mqtt", 6144, nullptr, 1, nullptr, 0) == pdPASS;
}

bool isMqttConnected() {
  return mqttConnected.load();
}

uint32_t mqttDisconnectCount() {
  return disconnectCount.load();
}
