#include "LocalControlCommand.h"

#include <cstring>

bool parseLocalControlCommand(const char *line, LocalControlCommand &command) {
  if (std::strcmp(line, "AUTO") == 0) {
    command = LocalControlCommand{};
    return true;
  }
  if (std::strncmp(line, "MANUAL ", 7) != 0) {
    return false;
  }
  const char *digits = line + 7;
  int brightness = 0;
  unsigned int count = 0;
  while (*digits != '\0') {
    if (*digits < '0' || *digits > '9' || ++count > 3) {
      return false;
    }
    brightness = brightness * 10 + (*digits++ - '0');
  }
  if (count == 0 || brightness > 100) {
    return false;
  }
  command.manual = true;
  command.brightness = brightness;
  return true;
}
