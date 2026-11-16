#!/usr/bin/env python3
"""Run firmware host checks in temporary directories without PlatformIO/Docker."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPILER = shutil.which('g++')
if not COMPILER:
    raise SystemExit('g++ is required for host checks; no tool is installed automatically')
JSON_INCLUDE = ROOT / '.pio/libdeps/esp32dev/ArduinoJson/src'
if not (JSON_INCLUDE / 'ArduinoJson.h').is_file():
    raise SystemExit('ArduinoJson 7.4.2 missing: run pio pkg install first')
CONTROL = ['src/LightingController.cpp', 'src/DimmingController.cpp', 'src/FaultDetector.cpp']
SUITES = [
    ('protocol', CONTROL + ['src/MqttProtocol.cpp', 'test/host/MqttProtocolChecks.cpp'], ['src']),
    ('controller', CONTROL + ['test/host/LightingControllerChecks.cpp'], ['src']),
    ('sensors', ['src/SensorReader.cpp', 'test/host/SensorReaderChecks.cpp'], ['test/host', 'src']),
    ('app', CONTROL + ['src/MqttProtocol.cpp', 'src/LocalControlCommand.cpp', 'src/FirmwareApp.cpp', 'test/host/FirmwareAppChecks.cpp'],
     ['test/host/runtime', 'src']),
    ('mqtt', CONTROL + ['src/MqttProtocol.cpp', 'test/host/ConnectivityChecks.cpp'], ['test/host/runtime', 'src']),
]


def run_checks():
    with tempfile.TemporaryDirectory(prefix='task006-checks-') as folder:
        for name, sources, includes in SUITES:
            executable = str(Path(folder) / (name + ('.exe' if sys.platform == 'win32' else '')))
            print(f'CHECK {name}', flush=True)
            command = [COMPILER, '-std=c++17', '-Wall', '-Wextra', '-Werror']
            command += [f'-I{include}' for include in includes] + [f'-I{JSON_INCLUDE}']
            subprocess.run(command + sources + ['-o', executable], cwd=ROOT, check=True)
            subprocess.run([executable], cwd=ROOT, check=True)
    print('PASS: all 5 host suites; hardware, RTOS timing and Wokwi live remain separate checks', flush=True)


if __name__ == '__main__':
    try:
        run_checks()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
