// Actual Connectivity implementation; deterministic transport/RTOS/clock stubs.
#include "../../src/Connectivity.cpp"
#include <ArduinoJson.h>
#include <cassert>
#include <cstdio>
#include <string>

FakeSerial Serial;
FakeWiFi WiFi;
namespace {
uint32_t networkNow = 0;
bool created = false;
struct TaskYield {};
size_t packetCount(const char *topic) {
  size_t count = 0;
  for (const auto &packet : mqtt.packets) {
    count += packet.topic == topic;
  }
  return count;
}
void step(uint32_t now) {
  networkNow = now;
  networkStep();
}
void receive(const std::string &payload) {
  char topic[sizeof(MqttProtocol::COMMAND_TOPIC)];
  std::strcpy(topic, MqttProtocol::COMMAND_TOPIC);
  mqtt.callback(topic, reinterpret_cast<uint8_t *>(const_cast<char *>(payload.data())), payload.size());
}
const std::string COMMAND = std::string("{\"schema_version\":1,\"node_id\":\"") + MqttProtocol::NODE_ID +
                            "\",\"boot_id\":\"b7e28a10\",\"command_id\":\"4113a6c8-27a4-4b2d-a37c-2a7956d673aa\","
                            "\"deadline_uptime_ms\":5000,\"mode\":\"MANUAL\",\"brightness\":80}";
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
  using namespace MqttProtocol;
  assert(startConnectivity() && created && !isMqttConnected());
  assert(std::string(mqttBootId()) == "b7e28a10");
  try {
    networkTask(nullptr);
  } catch (const TaskYield &) {
  }
  TelemetrySnapshot snapshot;
  snapshot.sensors.currentAdc = 4095;
  updateMqttSnapshot(snapshot);
  step(1000);
  assert(mqtt.clientId == std::string("smartlight-node_0") + std::to_string(SMARTLIGHT_NODE_INDEX) + "-p0");
  assert(isMqttConnected() && mqtt.subscribedQos == 1 && mqtt.subscribedTopic == COMMAND_TOPIC);
  assert(mqtt.subscriptions.size() == 2 && mqtt.subscriptions[0] == PING_TOPIC);
  assert(mqtt.cleanSession && mqtt.willRetain && mqtt.willQos == 0 && mqtt.willTopic == AVAILABILITY_TOPIC);
  JsonDocument doc;
  deserializeJson(doc, mqtt.willPayload);
  assert(doc["status"] == "OFFLINE" && doc["boot_id"] == mqttBootId());
  step(1001);
  assert(packetCount(AVAILABILITY_TOPIC) == 1 && packetCount(TELEMETRY_TOPIC) == 1);
  assert(mqtt.packets[0].retained && !mqtt.packets[1].retained);
  for (uint32_t now = 1010; now < 2000; now += 10) {
    snapshot.uptimeMs = now;
    snapshot.control.brightnessApplied = now % 101;
    updateMqttSnapshot(snapshot);
    step(now);
  }
  assert(packetCount(TELEMETRY_TOPIC) == 5); // 200ms spacing, no >5/s burst
  step(2999);
  step(3000);
  assert(packetCount(HEARTBEAT_TOPIC) == 1);
  assert(mqtt.packets.back().topic == HEARTBEAT_TOPIC || packetCount(TELEMETRY_TOPIC) >= 5);
  char pingTopic[sizeof(NodeIdentity::PING_TOPIC)];
  std::strcpy(pingTopic, NodeIdentity::PING_TOPIC);
  uint8_t payload[] = {'A', 0, 'B'};
  mqtt.callback(pingTopic, payload, 3);
  assert(mqtt.packets.back().topic == PONG_TOPIC && mqtt.packets.back().payload == std::string("A\0B", 3));
  const size_t beforeRejected = mqtt.packets.size();
  uint8_t tooLong[65] = {};
  mqtt.callback(pingTopic, tooLong, 65);
  char other[] = "other";
  mqtt.callback(other, payload, 3);
  assert(mqtt.packets.size() == beforeRejected);
  receive(COMMAND);
  assert(packetCount(ACK_TOPIC) == 0); // network callback cannot acknowledge application
  RemoteCommand command;
  assert(takeRemoteCommand(command) && command.valid && command.session == mqttDisconnectCount());
  CommandResult result;
  std::strcpy(result.commandId, command.commandId);
  result.reason = CommandReason::None;
  result.session = command.session;
  assert(completeRemoteCommand(result));
  mqtt.publishSucceeds = false;
  step(3010);
  assert(packetCount(ACK_TOPIC) == 0);
  mqtt.publishSucceeds = true;
  step(3020);
  assert(packetCount(ACK_TOPIC) == 1);
  deserializeJson(doc, mqtt.packets.back().payload);
  // Find ACK independently of concurrent telemetry.
  for (const auto &packet : mqtt.packets) {
    if (packet.topic == ACK_TOPIC) {
      deserializeJson(doc, packet.payload);
      assert(doc["result"] == "APPLIED" && !packet.retained);
    }
  }
  receive(COMMAND);
  mqtt.connectedValue = false;
  mqtt.connectSucceeds = false;
  step(4000);
  assert(!isMqttConnected() && mqttDisconnectCount() == 1 && !takeRemoteCommand(command));
  assert(!completeRemoteCommand(result));
  step(4000);
  assert(retryMs == 2000);
  const auto connections = mqtt.connects;
  step(5999);
  assert(mqtt.connects == connections);
  step(6000);
  assert(retryMs == 4000);
  step(10000);
  assert(retryMs == 8000);
  step(18000);
  assert(retryMs == 10000);
  mqtt.connectSucceeds = true;
  mqtt.subscribeSucceeds = false;
  step(28000);
  assert(!isMqttConnected());
  mqtt.subscribeSucceeds = true;
  step(38000);
  assert(isMqttConnected() && retryMs == 1000 && std::string(mqttBootId()) == "b7e28a10");
  const size_t beforeReconnect = packetCount(TELEMETRY_TOPIC);
  step(38001);
  assert(packetCount(TELEMETRY_TOPIC) == beforeReconnect + 1);
  assert(packetCount(AVAILABILITY_TOPIC) >= 2);
  const size_t ackCount = packetCount(ACK_TOPIC);
  step(40000);
  assert(packetCount(ACK_TOPIC) == ackCount); // no stale result replay
  const size_t beforePeriodic = packetCount(TELEMETRY_TOPIC);
  step(40001);
  assert(packetCount(TELEMETRY_TOPIC) == beforePeriodic + 1); // exactly 2s, even with no state change
  uint64_t expectedSeq = 0;
  for (const auto &packet : mqtt.packets) {
    if (packet.topic == TELEMETRY_TOPIC) {
      deserializeJson(doc, packet.payload);
      assert(doc["seq"].as<uint64_t>() == expectedSeq++ && doc["boot_id"] == mqttBootId());
    }
  }
  mqtt.loopSucceeds = false;
  step(40010);
  assert(!isMqttConnected());
  mqtt.loopSucceeds = true;
  step(41010);
  assert(isMqttConnected());
  WiFi.currentStatus = 0;
  step(41020);
  assert(!isMqttConnected() && !mqtt.connected());
  WiFi.currentStatus = WL_CONNECTED;
  step(42010);
  assert(isMqttConnected());
  step(42011); // force the first snapshot of the new session
  const size_t sensorBaseline = packetCount(TELEMETRY_TOPIC);
  snapshot.sensors.ldrAdc = 2345;
  updateMqttSnapshot(snapshot);
  step(42100);
  assert(packetCount(TELEMETRY_TOPIC) == sensorBaseline); // still within the 200ms limit
  step(42211);
  assert(packetCount(TELEMETRY_TOPIC) == sensorBaseline + 1); // raw changed, control did not
  deserializeJson(doc, mqtt.packets.back().payload);
  assert(doc["ldr_adc"] == 2345 && doc["node_id"] == NODE_ID);
  snapshot.sensors.ldrAdc = 3456;
  updateMqttSnapshot(snapshot);
  step(42300);
  snapshot.sensors.ldrAdc = 3457;
  updateMqttSnapshot(snapshot);
  step(42350);
  assert(packetCount(TELEMETRY_TOPIC) == sensorBaseline + 1);
  step(42411);
  assert(packetCount(TELEMETRY_TOPIC) == sensorBaseline + 2);
  deserializeJson(doc, mqtt.packets.back().payload);
  assert(doc["ldr_adc"] == 3457); // intermediate sensor samples coalesce to the latest value
  ++snapshot.sensors.analogSequence;
  updateMqttSnapshot(snapshot);
  step(42611);
  assert(packetCount(TELEMETRY_TOPIC) == sensorBaseline + 2); // counters alone cannot trigger a packet
  fakeEspTimeUs = 5000000000123LL;
  assert(firmwareUptimeMs() == 5000000000ULL);
  std::puts("PASS MQTT integration: diagnostics, clean/LWT/QoS/subscriptions, telemetry rate/seq/reconnect, ACK after result, publish failure retry, session "
            "flush, offline backoff, uptime64");
}
