#!/usr/bin/env python3
"""Run TASK-006 host checks in temporary directories without PlatformIO/Docker."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
COMPILER = shutil.which('g++')
if not COMPILER:
    raise SystemExit('g++ is required for host checks; no tool is installed automatically')
CONTROL = ['src/LightingController.cpp', 'src/DimmingController.cpp', 'src/FaultDetector.cpp']
SUITES = [
    ('controller', CONTROL + ['test/host/LightingControllerChecks.cpp'], ['src']),
    ('sensors', ['src/SensorReader.cpp', 'test/host/SensorReaderChecks.cpp'], ['test/host', 'src']),
    ('app', CONTROL + ['src/LocalControlCommand.cpp', 'src/FirmwareApp.cpp', 'test/host/FirmwareAppChecks.cpp'],
     ['test/host/runtime', 'src']),
    ('mqtt', ['test/host/ConnectivityChecks.cpp'], ['test/host/runtime', 'src']),
]


def run_checks():
    with tempfile.TemporaryDirectory(prefix='task006-checks-') as folder:
        for name, sources, includes in SUITES:
            executable = str(Path(folder) / (name + ('.exe' if sys.platform == 'win32' else '')))
            print(f'CHECK {name}', flush=True)
            command = [COMPILER, '-std=c++17', '-Wall', '-Wextra', '-Werror']
            command += [f'-I{include}' for include in includes]
            subprocess.run(command + sources + ['-o', executable], cwd=ROOT, check=True)
            subprocess.run([executable], cwd=ROOT, check=True)
    print('PASS: all 4 host suites; hardware, RTOS timing and Wokwi live remain separate checks', flush=True)


if __name__ == '__main__':
    try:
        run_checks()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
