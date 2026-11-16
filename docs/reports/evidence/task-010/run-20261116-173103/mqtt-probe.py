"""Bounded live MQTT probe using stdlib; never publishes telemetry or commands."""
import datetime
import json
import socket
import struct
import time
import uuid


def log(event, **values):
    print(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          monotonic_ns=time.monotonic_ns(), event=event, **values)), flush=True)


def field(value):
    data = value.encode()
    return struct.pack('!H', len(data)) + data


def packet(header, data):
    length = len(data)
    encoded = bytearray()
    while True:
        digit = length % 128
        length //= 128
        encoded.append(digit | (128 if length else 0))
        if not length:
            break
    return bytes([header]) + encoded + data


def exact(connection, length):
    data = b''
    while len(data) < length:
        block = connection.recv(length - len(data))
        if not block:
            raise ConnectionError('broker closed connection')
        data += block
    return data


def receive(connection):
    header = exact(connection, 1)[0]
    length, multiplier = 0, 1
    for _ in range(4):
        digit = exact(connection, 1)[0]
        length += (digit & 127) * multiplier
        if not digit & 128:
            return header, exact(connection, length)
        multiplier *= 128
    raise ValueError('invalid remaining length')


probe_id = 'task010-' + uuid.uuid4().hex[:12]
diagnostic = 'huit/nhom7/smartlight/v1/diagnostics/' + probe_id
with socket.create_connection(('127.0.0.1', 1883), timeout=3) as connection:
    connection.sendall(packet(0x10, field('MQTT') + b'\x04\x02\x00\x3c' + field(probe_id)))
    header, body = receive(connection)
    log('CONNACK', header=header, body=body.hex())
    assert header == 0x20 and body == b'\x00\x00'
    connection.sendall(packet(0x82, b'\x00\x01' + field('huit/nhom7/smartlight/v1/node_01/#')
                              + b'\x00' + field(diagnostic) + b'\x00'))
    header, body = receive(connection)
    log('SUBACK', header=header, body=body.hex())
    assert header == 0x90 and body[:2] == b'\x00\x01' and body[2:] == b'\x00\x00'
    connection.sendall(packet(0x30, field(diagnostic) + probe_id.encode()))
    log('DIAGNOSTIC_SENT', topic=diagnostic, payload=probe_id, retain=False)
    deadline, count, echo = time.monotonic() + 20, 0, False
    while time.monotonic() < deadline:
        connection.settimeout(min(1, max(.01, deadline - time.monotonic())))
        try:
            header, body = receive(connection)
        except socket.timeout:
            continue
        if header >> 4 == 3:
            length = int.from_bytes(body[:2], 'big')
            topic = body[2:2+length].decode()
            offset = 2 + length
            qos = (header >> 1) & 3
            if qos:
                packet_id = body[offset:offset+2]
                offset += 2
                if qos == 1:
                    connection.sendall(b'\x40\x02' + packet_id)
            payload = body[offset:].decode('utf-8', errors='replace')
            log('PUBLISH', topic=topic, payload=payload, retain=bool(header & 1), qos=qos)
            echo |= topic == diagnostic and payload == probe_id
            count += topic.endswith('/telemetry')
    connection.sendall(b'\xe0\x00')
    log('SUMMARY', diagnostic_echo=echo, telemetry_count=count, observation_seconds=20)
    assert echo, 'diagnostic pub/sub roundtrip failed'
