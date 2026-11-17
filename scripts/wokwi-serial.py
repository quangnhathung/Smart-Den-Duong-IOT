#!/usr/bin/env python3
"""Send local A2 commands over Wokwi RFC2217 and capture real Serial replies."""
import argparse
from datetime import datetime
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/reports/evidence/task-006'


class Verification:
    """Observe replies after LOCAL acceptance; no generated success lines from the node."""
    def __init__(self, mode, brightness=None, check_timeout=False):
        self.mode = mode
        self.brightness = brightness
        self.check_timeout = check_timeout
        self.accepted = False
        self.first_manual = None
        self.last_uptime = None
        self.applied = False

    def observe(self, line):
        if 'LOCAL command accepted=0' in line:
            raise ValueError('Firmware rejected command; MANUAL requires mqtt=1 and integer 0..100.')
        if 'LOCAL command accepted=1' in line:
            if self.accepted:
                raise ValueError('Another command was accepted during capture; timeout result is ambiguous.')
            self.accepted = True
            return False
        if self.accepted and ('P2/A2 lighting control' in line or 'rst:' in line):
            raise ValueError('ESP32 restarted during verification.')
        if not self.accepted or not line.startswith('CONTROL '):
            return False
        fields = dict(re.findall(r'(\w+)=([^\s]+)', line))
        uptime = int(fields['uptime_ms'])
        if self.last_uptime is not None and uptime < self.last_uptime:
            raise ValueError('Uptime decreased/wrapped; cannot confirm the same boot in this capture.')
        self.last_uptime = uptime
        if self.mode == 'AUTO':
            return fields.get('mode') == 'AUTO'
        if fields.get('mqtt') != '1':
            raise ValueError('MQTT is disconnected; fallback cannot be attributed to the 60s timer.')
        if fields.get('mode') == 'MANUAL':
            if int(fields['target']) != self.brightness:
                raise ValueError('MANUAL target differs from command.')
            if self.first_manual is None:
                self.first_manual = uptime
            self.applied |= int(fields['applied']) == self.brightness
            return self.applied and not self.check_timeout
        if self.check_timeout and fields.get('mode') == 'AUTO' and self.first_manual is not None:
            elapsed = uptime - self.first_manual
            # CONTROL is logged once per simulated second; command application is between lines.
            if not self.applied or not 59000 <= elapsed <= 61000:
                raise ValueError(f'AUTO returned after {elapsed}ms since first MANUAL log; outside 60s +/-1s log resolution.')
            return True
        raise ValueError('AUTO fallback before MANUAL was confirmed.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['MANUAL', 'AUTO', 'PROBE'])
    parser.add_argument('brightness', type=int, nargs='?')
    parser.add_argument('--check-timeout', action='store_true', help='observe MANUAL -> AUTO near 60 simulated seconds, MQTT staying connected')
    parser.add_argument('--wall-timeout', type=float, help='maximum wall seconds, default 30 or 300 for --check-timeout')
    parser.add_argument('--port', type=int, default=4000)
    args = parser.parse_args(argv)
    if args.mode == 'MANUAL' and (args.brightness is None or not 0 <= args.brightness <= 100):
        parser.error('MANUAL requires brightness 0..100')
    if args.mode != 'MANUAL' and (args.brightness is not None or args.check_timeout):
        parser.error('brightness and --check-timeout only apply to MANUAL')
    limit = args.wall_timeout if args.wall_timeout is not None else (300 if args.check_timeout else 30)
    if limit <= 0 or not 1 <= args.port <= 65535:
        parser.error('wall timeout must be positive and port must be 1..65535')
    try:
        import serial
    except ImportError:
        print('pyserial is missing; use the PlatformIO Python interpreter. Nothing was installed.', file=sys.stderr)
        return 2
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime('%Y%m%d-%H%M%S-%f')
    log_path = EVIDENCE / f'rfc2217-{args.mode.lower()}-{stamp}.log'
    with log_path.open('x', encoding='utf-8', newline='\n') as log:
        def record(kind, text):
            entry = f'{datetime.now().astimezone().isoformat(timespec="milliseconds")} {kind} {text}'
            print(entry, flush=True)
            log.write(entry + '\n')
            log.flush()

        record('HOST', f'endpoint=rfc2217://127.0.0.1:{args.port} log={log_path.name}')
        try:
            # Disable DTR/RTS before opening; do not deliberately reset the ESP32.
            connection = serial.serial_for_url(f'rfc2217://127.0.0.1:{args.port}', baudrate=115200, timeout=0.2, do_not_open=True)
            connection.dtr = False
            connection.rts = False
            with connection:
                record('HOST', 'RFC2217 negotiation succeeded')
                if args.mode == 'PROBE':
                    return 0
                command = f'MANUAL {args.brightness}' if args.mode == 'MANUAL' else 'AUTO'
                data = (command + '\n').encode('ascii')
                if connection.write(data) != len(data):
                    raise ValueError('Short serial write; command not fully sent.')
                record('TX', repr(data))
                verifier = Verification(args.mode, args.brightness, args.check_timeout)
                deadline = time.monotonic() + limit
                pending = bytearray()
                while time.monotonic() < deadline:
                    byte = connection.read(1)
                    if not byte:
                        continue
                    pending.extend(byte)
                    if len(pending) > 4096:
                        raise ValueError('Serial line exceeds 4096 bytes; refusing ambiguous output.')
                    if byte == b'\n':
                        line = bytes(pending).decode('utf-8', errors='replace').rstrip('\r\n')
                        pending.clear()
                        record('RX', line)
                        if verifier.observe(line):
                            record('RESULT', 'PASS observed requested mode/applied level' if not args.check_timeout
                                   else 'PASS observed MANUAL/applied then AUTO near 60s simulated (+/-1s CONTROL resolution), mqtt=1')
                            return 0
                raise ValueError('Wall timeout waiting for firmware confirmation; keep Wokwi visible/unpaused. No PASS recorded.')
        except (serial.SerialException, OSError, ValueError, KeyboardInterrupt) as error:
            record('RESULT', f'INCOMPLETE/FAIL: {error}')
            print(f'Check the selected Wokwi simulation uses rfc2217ServerPort={args.port}. No firmware/broker was changed.', file=sys.stderr)
            return 1


if __name__ == '__main__':
    raise SystemExit(main())
