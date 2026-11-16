#pragma once

#include <stdint.h>
constexpr int WL_CONNECTED = 3;
constexpr int WIFI_STA = 1;
struct WiFiClient {
  unsigned long timeout = 0;
  void setConnectionTimeout(unsigned long value) {
    timeout = value;
  }
};
struct FakeWiFi {
  int currentStatus = WL_CONNECTED;
  unsigned int reconnects = 0;
  void mode(int) {}
  void setAutoReconnect(bool) {}
  void begin(const char *, const char *, int) {}
  int status() {
    return currentStatus;
  }
  bool reconnect() {
    ++reconnects;
    return true;
  }
};
extern FakeWiFi WiFi;
