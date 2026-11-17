#pragma once

#ifndef SMARTLIGHT_NODE_INDEX
#define SMARTLIGHT_NODE_INDEX 1
#endif

#if SMARTLIGHT_NODE_INDEX == 1
#define SMARTLIGHT_NODE_ID "node_01"
#elif SMARTLIGHT_NODE_INDEX == 2
#define SMARTLIGHT_NODE_ID "node_02"
#elif SMARTLIGHT_NODE_INDEX == 3
#define SMARTLIGHT_NODE_ID "node_03"
#else
#error "SMARTLIGHT_NODE_INDEX must be 1, 2 or 3"
#endif

namespace NodeIdentity {
constexpr char NODE_ID[] = SMARTLIGHT_NODE_ID;
constexpr char CLIENT_ID[] = "smartlight-" SMARTLIGHT_NODE_ID "-p0";
constexpr char COMMAND_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/command";
constexpr char TELEMETRY_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/telemetry";
constexpr char ACK_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/ack";
constexpr char AVAILABILITY_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/availability";
constexpr char PING_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/diagnostics/ping";
constexpr char PONG_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/diagnostics/pong";
constexpr char HEARTBEAT_TOPIC[] = "huit/nhom7/smartlight/v1/" SMARTLIGHT_NODE_ID "/diagnostics/heartbeat";
} // namespace NodeIdentity

#undef SMARTLIGHT_NODE_ID
