#!/usr/bin/env python3
"""Copy a successful esp32dev build for node_01, checking freshness and hashes."""
import hashlib
from pathlib import Path
import shutil


def prepare(root):
    files = [root / '.pio/build/esp32dev' / name for name in ('firmware.bin', 'firmware.elf')]
    for path in files:
        if not path.is_file() or not path.stat().st_size:
            raise RuntimeError(f'Missing or empty artifact: {path}; build esp32dev first')
    inputs = [root / 'platformio.ini']
    for folder in ('src', 'include', 'lib'):
        inputs.extend(p for p in (root / folder).rglob('*') if p.is_file())
    newest = max(p.stat().st_mtime_ns for p in inputs)
    if any(p.stat().st_mtime_ns < newest for p in files):
        raise RuntimeError('Artifacts are older than project inputs; build esp32dev successfully first')
    destination = root / 'simulations/node_01/build'
    destination.mkdir(parents=True, exist_ok=True)
    for path in files:
        target = destination / path.name
        shutil.copy2(path, target)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'Checksum mismatch: {target}')
        print(f'{target.name} SHA-256 {digest}')


if __name__ == '__main__':
    try:
        prepare(Path(__file__).resolve().parents[1])
    except (OSError, RuntimeError) as error:
        raise SystemExit(str(error))
