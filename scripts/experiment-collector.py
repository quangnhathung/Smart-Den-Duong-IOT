#!/usr/bin/env python3
"""Durable TASK-012 observer. Read-only Serial; MQTT subscription; HTTP probes."""

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import signal
import sys
import threading
import time
from urllib.error import HTTPError
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    args = parser.parse_args()
    config = json.loads(args.runtime.read_text())
    qa = Path(config["qa"])
    host_boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    # Reuse the already installed pure-Python pyserial; do not install into a product venv.
    if config.get("serial_module_dir"):
        sys.path.insert(0, config["serial_module_dir"])
    import serial
    import paho.mqtt.client as mqtt

    stop = threading.Event()
    lock = threading.RLock()
    state = {"serial": {}, "telemetry": {}, "availability": {}, "health": None,
             "mqtt_connected": False, "errors": [], "started_at": datetime.now(timezone.utc).isoformat()}
    streams = {name: (qa / (name + ".jsonl")).open("a", buffering=1)
               for name in ("mqtt-events", "serial-events", "probe-events")}

    def record(stream, event, **data):
        row = dict(event=event, host_ms=time.time()*1000, monotonic_ns=time.monotonic_ns(),
                   host_boot_id=host_boot_id, **data)
        with lock:
            streams[stream].write(json.dumps(row, allow_nan=False) + "\n")
        return row

    def serial_reader(index):
        node = f"node_0{index}"
        try:
            port = serial.serial_for_url(f"rfc2217://127.0.0.1:{3999+index}", baudrate=115200,
                                         timeout=.3, do_not_open=True)
            port.dtr = False
            port.rts = False
            port.open()
            pending = b""
            with port:
                while not stop.is_set():
                    pending += port.read(1024)
                    lines = pending.split(b"\n")
                    pending = lines.pop()
                    for line in lines:
                        text = line.decode(errors="replace").strip()
                        event = record("serial-events", "serial", node_id=node, line=text)
                        match = re.search(r"\buptime_ms=(\d+)", text)
                        if match:
                            with lock:
                                old = state["serial"].get(node, {})
                                if int(match[1]) >= old.get("uptime_ms", 0):
                                    state["serial"][node] = dict(uptime_ms=int(match[1]),
                                                                host_ms=event["host_ms"],
                                                                monotonic_ns=event["monotonic_ns"], line=text)
        except Exception as exc:
            record("serial-events", "error", node_id=node, error=str(exc))
            with lock:
                state["errors"].append(f"Serial {node}: {exc}")

    def on_connect(client, userdata, flags, reason, properties):
        record("mqtt-events", "connected", reason=str(reason))
        with lock:
            state["mqtt_connected"] = not reason.is_failure
        if not reason.is_failure:
            client.subscribe("huit/nhom7/smartlight/v1/#", qos=0)

    def on_disconnect(client, userdata, flags, reason, properties):
        record("mqtt-events", "disconnected", reason=str(reason))
        with lock:
            state["mqtt_connected"] = False

    def on_message(client, userdata, message):
        text = message.payload.decode(errors="replace")
        try:
            payload = json.loads(text)
        except ValueError:
            payload = text
        event = record("mqtt-events", "message", topic=message.topic, payload=payload,
                       retained=bool(message.retain))
        if isinstance(payload, dict) and payload.get("node_id") in ("node_01", "node_02", "node_03"):
            key = "telemetry" if message.topic.endswith("/telemetry") else "availability" if message.topic.endswith("/availability") else None
            if key:
                with lock:
                    state[key][payload["node_id"]] = event

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="task012-observer-"+qa.name[-6:])
    client.on_connect, client.on_disconnect, client.on_message = on_connect, on_disconnect, on_message
    client.reconnect_delay_set(1, 2)
    client.connect_async("127.0.0.1", 1883, keepalive=15)
    client.loop_start()

    def probe():
        while not stop.is_set():
            for endpoint in ("health", "nodes"):
                try:
                    try:
                        response = urlopen(config["api"]+"/api/"+endpoint, timeout=4)
                    except HTTPError as exc:
                        response = exc
                    with response:
                        value = json.loads(response.read())
                        code = response.status
                    event = record("probe-events", endpoint, status_code=code, value=value)
                    if endpoint == "health":
                        with lock:
                            state["health"] = event
                except Exception as exc:
                    record("probe-events", "error", endpoint=endpoint, error=str(exc))
            stop.wait(2)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/state":
                self.send_error(404)
                return
            with lock:
                value = dict(state, heartbeat_monotonic_ns=time.monotonic_ns(), pid=__import__("os").getpid())
                data = json.dumps(value).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 18771), Handler)
    threads = [threading.Thread(target=serial_reader, args=(n,), daemon=True) for n in (1, 2, 3)]
    threads += [threading.Thread(target=probe, daemon=True), threading.Thread(target=server.serve_forever, daemon=True)]
    for thread in threads:
        thread.start()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    print("Collector listening127.0.0.1:18771", flush=True)
    while not stop.wait(1):
        with lock:
            (qa/"collector-heartbeat.json").write_text(json.dumps(dict(pid=__import__("os").getpid(),
                 monotonic_ns=time.monotonic_ns(), serial_nodes=list(state["serial"]), errors=state["errors"]))+"\n")
    server.shutdown()
    client.disconnect()
    client.loop_stop()
    for thread in threads:
        thread.join(timeout=2)
    for stream in streams.values():
        stream.close()


if __name__ == "__main__":
    main()
