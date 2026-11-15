#include "EnvironmentSmokeTest.h"

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <algorithm>
#include <esp_arduino_version.h>

namespace {
constexpr uint8_t LED_PIN = 26;
constexpr uint32_t PWM_INTERVAL_MS = 2000;
constexpr uint32_t LOG_INTERVAL_MS = 1000;
constexpr uint32_t LOOP_IDLE_MS = 10;
constexpr uint32_t HEARTBEAT_INTERVAL_MS = 2000;
constexpr uint16_t MQTT_KEEPALIVE_SECONDS = 15;
constexpr uint8_t LEVELS[] = {0, 25, 50, 70, 100};
constexpr char PING_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/ping";
constexpr char PONG_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/pong";
constexpr char HEARTBEAT_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/heartbeat";
WiFiClient networkClient;
PubSubClient mqtt(networkClient);
uint32_t lastPwmMs = 0;
uint32_t lastLogMs = 0;
uint32_t lastAttemptMs = 0;
uint32_t lastHeartbeatMs = 0;
uint32_t retryMs = 1000;
size_t levelIndex = 0;
bool pwmReady = false;
bool mqttReady = false;
bool wasMqttConnected = false;

void logMqttTransition() {
  const bool connected = mqtt.connected();
  if (connected != wasMqttConnected) {
    Serial.printf("uptime_ms=%lu MQTT %s state=%d wifi=%d\n", static_cast<unsigned long>(millis()), connected ? "connected" : "disconnected", mqtt.state(),
                  WiFi.status());
    wasMqttConnected = connected;
  }
}

void publishHeartbeat(uint32_t now) {
  if (now - lastHeartbeatMs < HEARTBEAT_INTERVAL_MS) {
    return;
  }
  lastHeartbeatMs = now;
  char payload[48];
  const int length = snprintf(payload, sizeof(payload), "{\"uptime_ms\":%lu}", static_cast<unsigned long>(now));
  const bool sent = length > 0 && static_cast<size_t>(length) < sizeof(payload) && mqtt.publish(HEARTBEAT_TOPIC, payload, false);
  Serial.printf("uptime_ms=%lu HEARTBEAT published=%d state=%d\n", static_cast<unsigned long>(now), sent, mqtt.state());
}

void applyLevel() {
  const uint8_t percent = LEVELS[levelIndex];
  const uint8_t duty = (percent * 255U + 50U) / 100U;
  if (pwmReady && !ledcWrite(LED_PIN, duty)) {
    Serial.println("PWM write failed");
  }
  Serial.printf("PWM requested=%u%% duty=%u ready=%d\n", percent, duty, pwmReady);
}

void receivePing(char *topic, uint8_t *payload, unsigned int length) {
  if (strcmp(topic, PING_TOPIC) != 0 || length > 64) {
    Serial.println("PING rejected: topic or length");
    return;
  }
  uint8_t copy[64];
  memcpy(copy, payload, length);
  const bool sent = mqtt.publish(PONG_TOPIC, copy, length, false);
  Serial.printf("PING bytes=%u PONG published=%d\n", length, sent);
}
} // namespace

void setupSmokeTest() {
  Serial.begin(115200);
  Serial.printf("P0 smoke node_01 Arduino=%s; diagnostic firmware only\n", ESP_ARDUINO_VERSION_STR);
  pwmReady = ledcAttach(LED_PIN, 5000, 8);
  applyLevel();
  networkClient.setConnectionTimeout(1000);
  mqtt.setServer("host.wokwi.internal", 1883);
  mqtt.setSocketTimeout(1);
  mqtt.setKeepAlive(MQTT_KEEPALIVE_SECONDS);
  mqtt.setCallback(receivePing);
  mqttReady = mqtt.setBufferSize(2048);
  if (!mqttReady) {
    Serial.println("MQTT buffer allocation failed; PWM remains active");
  }
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(false);
  WiFi.begin("Wokwi-GUEST", "", 6);
}

void loopSmokeTest() {
  // Short cooperative sleep for Wokwi; this is diagnostic P0 firmware.
  delay(LOOP_IDLE_MS);
  const uint32_t now = millis();
  logMqttTransition();
  if (now - lastPwmMs >= PWM_INTERVAL_MS) {
    lastPwmMs = now;
    levelIndex = (levelIndex + 1) % (sizeof(LEVELS) / sizeof(LEVELS[0]));
    applyLevel();
  }
  if (now - lastLogMs >= LOG_INTERVAL_MS) {
    lastLogMs = now;
    Serial.printf("uptime_ms=%lu wifi=%d mqtt=%d state=%d\n", static_cast<unsigned long>(now), WiFi.status(), mqtt.connected(), mqtt.state());
  }
  if (mqttReady && WiFi.status() == WL_CONNECTED && mqtt.connected()) {
    retryMs = 1000;
    if (mqtt.loop()) {
      publishHeartbeat(millis());
    } else {
      Serial.printf("uptime_ms=%lu MQTT loop failed state=%d\n", static_cast<unsigned long>(millis()), mqtt.state());
    }
    logMqttTransition();
    return;
  }
  if (now - lastAttemptMs < retryMs) {
    return;
  }
  lastAttemptMs = now;
  if (WiFi.status() != WL_CONNECTED) {
    const bool started = WiFi.reconnect();
    Serial.printf("uptime_ms=%lu WiFi reconnect started=%d wifi=%d\n", static_cast<unsigned long>(millis()), started, WiFi.status());
  } else if (mqttReady) {
    Serial.printf("uptime_ms=%lu MQTT connect attempt retry_ms=%lu\n", static_cast<unsigned long>(now), static_cast<unsigned long>(retryMs));
    if (!mqtt.connect("smartlight-node_01-p0")) {
      Serial.printf("uptime_ms=%lu MQTT connect failed state=%d wifi=%d\n", static_cast<unsigned long>(millis()), mqtt.state(), WiFi.status());
      retryMs = std::min<uint32_t>(retryMs * 2U, 10000U);
      return;
    }
    logMqttTransition();
    if (!mqtt.subscribe(PING_TOPIC, 1)) {
      Serial.println("MQTT subscribe failed; retry connection");
      mqtt.disconnect();
      logMqttTransition();
    } else {
      Serial.println("MQTT connected; ping subscribed");
      retryMs = 1000;
      lastHeartbeatMs = millis();
      return;
    }
  }
  retryMs = std::min<uint32_t>(retryMs * 2U, 10000U);
}
