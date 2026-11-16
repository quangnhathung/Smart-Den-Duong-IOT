#pragma once

struct LocalControlCommand {
  bool manual = false;
  int brightness = 0;
};

// Local Serial test interface only. This does not parse MQTT command v1.
bool parseLocalControlCommand(const char *line, LocalControlCommand &command);
