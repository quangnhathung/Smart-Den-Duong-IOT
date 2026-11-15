#include "EnvironmentSmokeTest.h"

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <esp_arduino_version.h>

namespace {
constexpr uint8_t LED_PIN = 26;
constexpr uint32_t PWM_INTERVAL_MS = 2000;
constexpr uint32_t LOG_INTERVAL_MS = 1000;
constexpr uint8_t LEVELS[] = {0, 25, 50, 70, 100};
constexpr char PING_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/ping";
constexpr char PONG_TOPIC[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/pong";
WiFiClient networkClient;
PubSubClient mqtt(networkClient);
uint32_t lastPwmMs = 0;
uint32_t lastLogMs = 0;
uint32_t lastAttemptMs = 0;
uint32_t retryMs = 1000;
size_t levelIndex = 0;
bool pwmReady = false;
bool mqttReady = false;

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
  const uint32_t now = millis();
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
    mqtt.loop();
    return;
  }
  if (now - lastAttemptMs < retryMs) {
    return;
  }
  lastAttemptMs = now;
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
  } else if (mqttReady && mqtt.connect("smartlight-node_01-p0")) {
    if (!mqtt.subscribe(PING_TOPIC, 1)) {
      Serial.println("MQTT subscribe failed; retry connection");
      mqtt.disconnect();
    } else {
      Serial.println("MQTT connected; ping subscribed");
      retryMs = 1000;
      return;
    }
  }
  retryMs = min(retryMs * 2U, 10000U);
}
