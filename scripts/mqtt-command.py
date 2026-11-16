#!/usr/bin/env python3
"""Generate a labeled MQTT test command from a freshly captured telemetry file; never publish."""
import argparse
import json
from pathlib import Path
import re
import sys
import time
import uuid


def make_command(telemetry, mode, brightness=None, case='valid'):
    if type(telemetry.get('schema_version')) is not int or telemetry.get('schema_version') != 1 or telemetry.get('node_id') != 'node_01':
        raise ValueError('Expected schema v1 telemetry for node_01')
    boot = telemetry.get('boot_id')
    uptime = telemetry.get('uptime_ms')
    if not isinstance(boot, str) or not re.fullmatch(r'[0-9a-fA-F]{8}', boot):
        raise ValueError('Missing/invalid boot_id')
    if type(uptime) is not int or not 0 <= uptime <= (1 << 64) - 5001:
        raise ValueError('Missing/invalid uint64 uptime_ms')
    if mode not in ('AUTO', 'MANUAL'):
        raise ValueError('mode must be AUTO or MANUAL')
    if mode == 'MANUAL' and (type(brightness) is not int or not 0 <= brightness <= 100):
        raise ValueError('MANUAL needs integer brightness 0..100')
    if mode == 'AUTO' and brightness is not None:
        raise ValueError('AUTO must not include brightness')
    result = dict(schema_version=1, node_id='node_01', boot_id=boot.lower(), command_id=str(uuid.uuid4()),
                  deadline_uptime_ms=uptime + 5000, mode=mode)
    if mode == 'MANUAL':
        result['brightness'] = brightness
    if case == 'expired':
        result['deadline_uptime_ms'] = 0
    elif case == 'wrong-boot':
        result['boot_id'] = '00000001' if boot.lower() == '00000000' else '00000000'
    elif case == 'wrong-node':
        result['node_id'] = 'node_02'
    elif case == 'invalid-brightness':
        result['mode'] = 'MANUAL'
        result['brightness'] = 101
    elif case != 'valid':
        raise ValueError('Unknown fixture case')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--telemetry', type=Path, required=True, help='Fresh mosquitto_sub payload, without topic prefix')
    parser.add_argument('--mode', choices=['AUTO', 'MANUAL'], required=True)
    parser.add_argument('--brightness', type=int)
    parser.add_argument('--case', choices=['valid', 'expired', 'wrong-boot', 'wrong-node', 'invalid-brightness'], default='valid')
    args = parser.parse_args(argv)
    try:
        age = time.time() - args.telemetry.stat().st_mtime
        if not 0 <= age <= 3:
            raise ValueError('Telemetry capture older than 3 seconds or future-dated; capture a fresh packet')
        # utf-8-sig supports Windows PowerShell redirected UTF-8 files with BOM.
        telemetry = json.loads(args.telemetry.read_text(encoding='utf-8-sig'))
        if not isinstance(telemetry, dict):
            raise ValueError('Expected telemetry JSON object')
        print(json.dumps(make_command(telemetry, args.mode, args.brightness, args.case), separators=(',', ':')))
    except (OSError, ValueError) as error:
        print(f'Command not generated: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
