// Compile the actual task implementation in this TU to exercise its steps without an RTOS.
#include "../../src/Connectivity.cpp"

#include <cassert>
#include <cstdio>

FakeSerial Serial;
FakeWiFi WiFi;
namespace {
uint32_t networkNow = 0;
bool created = false;
struct TaskYield {};
} // namespace
unsigned long millis() {
  return networkNow;
}
int xTaskCreatePinnedToCore(void (*task)(void *), const char *, unsigned long stack, void *, int priority, void *, int core) {
  assert(task == networkTask && stack >= 4096 && priority == 1 && core == 0);
  created = true;
  return pdPASS;
}
void vTaskDelay(unsigned long ticks) {
  assert(ticks == 10);
  throw TaskYield{};
}

int main() {
  assert(startConnectivity() && created && !isMqttConnected());
  try {
    networkTask(nullptr);
  } catch (const TaskYield &) {
  }
  networkNow = 1000;
  networkStep();
  assert(isMqttConnected() && mqtt.subscribedQos == 1 && mqtt.subscribedTopic == PING_TOPIC);
  networkNow = 2999;
  networkStep();
  assert(mqtt.packets.empty());
  networkNow = 3000;
  networkStep();
  assert(mqtt.packets.size() == 1 && mqtt.packets[0].topic == HEARTBEAT_TOPIC);
  assert(mqtt.packets[0].payload == "{\"uptime_ms\":3000}" && !mqtt.packets[0].retained);
  char pingTopic[] = "huit/nhom7/smartlight/v1/node_01/diagnostics/ping";
  uint8_t payload[] = {'A', 0, 'B'};
  mqtt.callback(pingTopic, payload, 3);
  assert(mqtt.packets.back().topic == PONG_TOPIC && mqtt.packets.back().payload.size() == 3);
  assert(mqtt.packets.back().payload[0] == 'A' && mqtt.packets.back().payload[1] == 0 && mqtt.packets.back().payload[2] == 'B');
  assert(!mqtt.packets.back().retained);
  const auto beforeRejected = mqtt.packets.size();
  uint8_t tooLong[65] = {};
  mqtt.callback(pingTopic, tooLong, 65);
  char wrongTopic[] = "other";
  mqtt.callback(wrongTopic, payload, 3);
  assert(mqtt.packets.size() == beforeRejected);
  mqtt.connectedValue = false;
  mqtt.connectSucceeds = false;
  networkNow = 4000;
  networkStep();
  assert(!isMqttConnected() && mqttDisconnectCount() == 1);
  networkStep();
  assert(!isMqttConnected() && retryMs == 2000);
  const auto connections = mqtt.connects;
  networkNow = 5999;
  networkStep();
  assert(mqtt.connects == connections);
  networkNow = 6000;
  networkStep();
  assert(retryMs == 4000);
  networkNow = 10000;
  networkStep();
  assert(retryMs == 8000);
  networkNow = 18000;
  networkStep();
  assert(retryMs == 10000);
  mqtt.connectSucceeds = true;
  mqtt.subscribeSucceeds = false;
  networkNow = 28000;
  networkStep();
  assert(!isMqttConnected());
  mqtt.subscribeSucceeds = true;
  networkNow = 38000;
  networkStep();
  assert(isMqttConnected() && retryMs == 1000);
  networkNow = 40000;
  networkStep();
  assert(mqtt.packets.back().topic == HEARTBEAT_TOPIC);
  mqtt.loopSucceeds = false;
  networkNow = 40010;
  networkStep();
  assert(!isMqttConnected());
  mqtt.loopSucceeds = true;
  networkNow = 41010;
  networkStep();
  assert(isMqttConnected());
  WiFi.currentStatus = 0;
  networkNow = 41020;
  networkStep();
  assert(!isMqttConnected() && !mqtt.connectedValue);
  WiFi.currentStatus = WL_CONNECTED;
  networkNow = 42010;
  networkStep();
  assert(isMqttConnected());
  std::puts("PASS MQTT task: preserved topics/binary ping-pong/64-byte bound/non-retain heartbeat, QoS1 subscribe, retry cap, reconnect/resubscribe, loop "
            "failure status");
}
