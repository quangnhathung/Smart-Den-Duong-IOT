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
            for index in ((1, 2, 3) if name in ('protocol', 'app', 'mqtt') else (1,)):
                label = f'{name}-node_0{index}'
                executable = str(Path(folder) / (label + ('.exe' if sys.platform == 'win32' else '')))
                print(f'CHECK {label}', flush=True)
                command = [COMPILER, '-std=c++17', '-Wall', '-Wextra', '-Werror', f'-DSMARTLIGHT_NODE_INDEX={index}']
                command += [f'-I{include}' for include in includes] + [f'-I{JSON_INCLUDE}']
                subprocess.run(command + sources + ['-o', executable], cwd=ROOT, check=True)
                subprocess.run([executable], cwd=ROOT, check=True)
        # A bad deployment identity must fail at compile time, before any firmware can run.
        for index in (0, 4):
            result = subprocess.run([COMPILER, '-std=c++17', '-Isrc', f'-DSMARTLIGHT_NODE_INDEX={index}',
                                     '-x', 'c++', '-fsyntax-only', '-'], input='#include "NodeIdentity.h"\n',
                                    cwd=ROOT, text=True, capture_output=True)
            if result.returncode == 0 or 'SMARTLIGHT_NODE_INDEX must be 1, 2 or 3' not in result.stderr:
                raise RuntimeError(f'Invalid node index {index} did not fail with the expected diagnostic')
    print('PASS: 11 host runs and 2 invalid identity checks; Wokwi live remains separate', flush=True)


if __name__ == '__main__':
    try:
        run_checks()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
