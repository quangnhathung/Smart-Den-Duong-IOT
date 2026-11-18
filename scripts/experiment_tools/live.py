"""Live runner with explicit ownership, durable attempt state and per-node windows."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, timezone
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import signal
import shutil
import sqlite3
import statistics
import subprocess
import time
import traceback
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .analysis import calculate, compare_stats
from .recipes import NODES, DURATIONS, actions, configuration, scene


def dump(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def request(base, path, body=None, timeout=8):
    req = Request(base+path, data=None if body is None else json.dumps(body).encode(),
                  headers={"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        data = response.read().decode()
        return json.loads(data) if "json" in response.headers.get("Content-Type", "") else data


def database(config):
    db = sqlite3.connect("file:" + config["database"] + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def observer():
    return request("http://127.0.0.1:18771", "/state", timeout=3)


def predicted_uptime(serial, rate, now_ns):
    """Bounded scheduling estimate only; raw timestamps remain the audit authority."""
    age_ms=max(0, (now_ns-serial["monotonic_ns"])/1e6)
    return serial["uptime_ms"]+min(1000, age_ms*max(.1,min(1.2,rate)))


def ui(config, node, kind, **values):
    return request(config["ui"], "/action", dict(node=NODES.index(node)+1, kind=kind, **values),timeout=30)


def configure_scene(config, node, value):
    lux = {"DAY": 100000, "TWILIGHT": config["calibration"]["twilight_lux"], "NIGHT": .1}[value["environment"]]
    return ui(config, node, "scene", lux=lux, distance=value["distance"], current=1023)


def preflight(config):
    health = request(config["api"], "/api/health")
    assert health["status"] == "OK" and health["dropped_events"] == 0, health
    nodes = request(config["api"], "/api/nodes")
    assert len(nodes) == 3 and all(n["connection"] == "ONLINE" and n["freshness"] == "FRESH" for n in nodes), nodes
    state = observer()
    assert not state["errors"] and state["mqtt_connected"], state
    assert set(state["serial"]) == set(NODES), state["serial"]
    assert all(time.monotonic_ns()-v["monotonic_ns"] < 6e9 for v in state["serial"].values()), "Serial stale"
    root = Path(config["root"])
    reference = root/"docs/reports/evidence/task-011/run-20261117-135233"
    for node in NODES:
        manifest = json.loads((reference/f"{node}-artifact-manifest-final.json").read_text())
        for name, expected in manifest["inputs_sha256"].items():
            assert hashlib.sha256((root/name).read_bytes()).hexdigest() == expected, name
        for name, value in manifest["artifacts"].items():
            assert hashlib.sha256((Path(config["qa"])/node/"build"/name).read_bytes()).hexdigest() == value["sha256"], (node, name)
    for node in NODES:
        assert state["telemetry"][node]["payload"]["boot_id"] == next(n for n in nodes if n["node_id"] == node)["telemetry"]["boot_id"]
    return dict(status="PASS", checked_at=datetime.now(timezone.utc).isoformat(), health=health, nodes=nodes,
                serial=state["serial"], source_and_artifacts_match_task011=True)


def owned_broker(config, operation):
    path = Path(config["qa"])/"owned-processes.json"
    owned = json.loads(path.read_text())
    entry = next(v for v in reversed(owned) if v["name"] == "broker")
    proc = Path(f"/proc/{entry['pid']}")
    if operation == "stop":
        assert proc.exists() and (proc/"stat").read_text().split()[21] == entry["proc_start_ticks"], "Broker PID changed"
        assert str(config["qa"]) in (proc/"cmdline").read_bytes().decode(), "Not an owned broker"
        os.kill(entry["pid"], signal.SIGTERM)
        end = time.monotonic()+8
        while proc.exists() and time.monotonic() < end:
            if (proc/"stat").read_text().split()[2] == "Z":
                break
            time.sleep(.05)
    elif operation == "start":
        # A new process is explicitly recorded; no old pending MQTT command is published.
        env = dict(os.environ, LD_LIBRARY_PATH=config["broker_library_dir"])
        args = [config["broker_binary"], "-c", config["broker_config"], "-v"]
        process = subprocess.Popen(args, env=env, stdout=(Path(config["qa"])/"broker.log").open("a"),
                                   stderr=subprocess.STDOUT, start_new_session=True)
        owned.append(dict(name="broker", pid=process.pid, args=args,
                          proc_start_ticks=Path(f"/proc/{process.pid}/stat").read_text().split()[21]))
        dump(path, owned)
    else:
        raise ValueError(operation)
    return dict(operation=operation, host_ms=time.time()*1000)


def latest_rows(config, earliest):
    with database(config) as db:
        return {node: db.execute("SELECT * FROM telemetry WHERE node_id=? AND received_at>=? AND quality='ACCEPTED' ORDER BY received_at,id LIMIT 1",
                                 (node, earliest)).fetchone() for node in NODES}


def perform(config, event):
    node, kind, value = event.node_id, event.kind, event.value
    before = observer()["serial"][node]
    offsets={name:(Path(config["qa"])/(name+".jsonl")).stat().st_size for name in ("mqtt-events","serial-events")}
    started = time.time()*1000
    if kind == "motion":
        result = ui(config, node, "motion")
    elif kind == "prepare-distance":
        result = ui(config, node, "prepare-scene", distance=value)
    elif kind == "prepare-scene":
        result = ui(config, node, "prepare-scene", lux={"DAY":100000,"TWILIGHT":config["calibration"]["twilight_lux"],"NIGHT":.1}[value["environment"]],distance=value["distance"])
    elif kind == "distance":
        result = ui(config, node, "scene", distance=value)
    elif kind == "scene":
        result = configure_scene(config, node, value)
    elif kind == "current":
        result = ui(config, node, "scene", current=value)
    elif kind == "broker":
        result = owned_broker(config, value)
    elif kind == "offline_ldr":
        result = ui(config, "node_01", "scene", lux=100000 if value == "DAY" else .1)
    else:
        raise ValueError(kind)
    finished = time.time()*1000
    after = observer()["serial"][node]
    confirmation=None
    if not kind.startswith("prepare-") and kind not in ("broker","offline_ldr"):
        effects=result.get("effects",[])
        if kind=="motion" or effects:
            deadline=time.monotonic()+5
            while time.monotonic()<deadline and confirmation is None:
                name="serial-events" if kind=="motion" else "mqtt-events"
                with (Path(config["qa"])/(name+".jsonl")).open("rb") as stream:
                    stream.seek(offsets[name]);raw=stream.read()
                for line in raw.splitlines():
                    try:sample=json.loads(line)
                    except ValueError:continue
                    if sample["host_ms"]<started:continue
                    if kind=="motion":
                        match=re.search(r"^PIR uptime_ms=(\d+) motion=1$",sample.get("line",""))
                        if sample.get("node_id")==node and match:
                            confirmation=dict(source="raw Serial PIR edge",uptime_ms=int(match[1]),host_ms=sample["host_ms"]);break
                    elif sample.get("topic","").endswith('/'+node+'/telemetry'):
                        payload=sample["payload"]
                        def matches(effect):
                            field,val=effect["kind"],effect["value"]
                            if field=="current":return payload["current_adc"]<20 if val==0 else payload["current_adc"]>=4000
                            if field=="distance":return payload["distance_cm"] is not None and abs(payload["distance_cm"]-val)<5
                            if field=="lux":return payload["ldr_adc"]>3900 if val==.1 else payload["ldr_adc"]<100 if val==100000 else 1850<=payload["ldr_adc"]<=2200
                            return False
                        if all(matches(effect) for effect in effects):
                            confirmation=dict(source="raw MQTT sensor sample",uptime_ms=payload["uptime_ms"],seq=payload["seq"],host_ms=sample["host_ms"]);break
                if confirmation is None:time.sleep(.05)
            if confirmation is None:raise RuntimeError(f"Missing physical input confirmation: {event}")
        else:
            confirmation=dict(source="No input change; desired value already set",uptime_ms=before["uptime_ms"],not_applicable=True)
    # Prepare the next pulse outside the timing interval of the physical change.
    if kind in ("distance", "scene"):
        ui(config, node, "arm-motion")
    if kind=="broker" and value=="stop":
        ui(config,"node_01","prepare-scene",lux=100000)
    return dict(recipe=asdict(event), started_host_ms=started, finished_host_ms=finished,
                before_clock=before, after_clock=after, result=result,physical_confirmation=confirmation)


def wait_ready(config, scenario):
    end = time.monotonic()+90
    while time.monotonic() < end:
        nodes = request(config["api"], "/api/nodes")
        if all(n["connection"] == "ONLINE" and n["freshness"] == "FRESH" and n["telemetry"] and
               n["telemetry"]["mode"] == "AUTO" and not n["telemetry"]["faults"] and
               n["telemetry"]["motion"] == "NONE" and n["telemetry"]["current_adc"] >= 3891 and
               n["telemetry"]["distance_cm"] is not None and abs(n["telemetry"]["distance_cm"]-scene(scenario,n["node_id"])["distance"])<5 and
               n["telemetry"]["environment"] == scene(scenario, n["node_id"])["environment"] and
               n["telemetry"]["brightness_applied"] == {"DAY": 0, "TWILIGHT": 50, "NIGHT": 25}[n["telemetry"]["environment"]]
               for n in nodes):
            return nodes
        time.sleep(.5)
    raise RuntimeError("Initial scene did not stabilize")


def collect_attempt(config, scenario, repeat):
    qa = Path(config["qa"])
    attempts = qa/"attempts"
    attempts.mkdir(exist_ok=True)
    number = len(list(attempts.glob(f"{scenario}-r{repeat:02}-a*")))+1
    folder = attempts/f"{scenario}-r{repeat:02}-a{number:02}"
    folder.mkdir()
    harness=folder/"harness"
    harness.mkdir()
    root=Path(config["root"])
    sources=[root/"scripts/experiments.py",root/"scripts/experiment-collector.py",
             root/"scripts/experiment-ui.cjs",root/"scripts/experiment-dashboard.cjs",
             *sorted((root/"scripts/experiment_tools").glob("*.py"))]
    hashes={}
    for source in sources:
        relative=source.relative_to(root/"scripts")
        target=harness/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        hashes[str(relative)]=hashlib.sha256(source.read_bytes()).hexdigest()
    dump(folder/"harness-sha256.json",hashes)
    recipe = configuration(scenario, repeat)
    result = dict(status="RUNNING", scenario=scenario, repeat=repeat, attempt=number,
                  configuration=recipe, errors=[], actions=[], windows={}, started_host_ms=time.time()*1000,
                  host_boot_id=Path("/proc/sys/kernel/random/boot_id").read_text().strip())
    dump(folder/"result.json", result)
    dump(qa/"campaign-status.json", dict(current=str(folder), status="PREPARING", scenario=scenario, repeat=repeat))
    experiment = None
    pool = ThreadPoolExecutor(max_workers=3)
    try:
        preflight(config)
        list(pool.map(lambda n: ui(config,n,"reset-cache"),NODES))
        list(pool.map(lambda n: configure_scene(config, n, scene(scenario, n)), NODES))
        wait_ready(config, scenario)
        list(pool.map(lambda n: ui(config, n, "arm-motion"), NODES))
        pre = preflight(config)
        dump(folder/"preflight.json", pre)
        for node in NODES:
            ui(config,node,"shot",name=folder.name+'-'+node+'-start.png')
        request("http://127.0.0.1:18773","/shot",dict(name=folder.name+'-dashboard-start.png'))
        name = f"TASK012 {folder.name} {datetime.now(timezone.utc).strftime('%H%M%S')}"
        experiment = request(config["api"], "/api/experiments", dict(name=name, configuration=recipe,
                             notes="Live Wokwi. Node uptime schedules; per-node windows finalized by accepted SQLite samples."))
        dump(folder/"experiment-start.json", experiment)
        epoch = datetime.fromisoformat(experiment["started_at"].replace("Z", "+00:00")).timestamp()
        end_wait = time.monotonic()+12
        while True:
            first = latest_rows(config, epoch)
            if all(first.values()):
                break
            if time.monotonic() > end_wait:
                raise RuntimeError("No accepted first sample for all nodes")
            time.sleep(.1)
        start = {n: dict(first[n]) for n in NODES}
        boots = {n: json.loads(start[n]["payload"])["boot_id"] for n in NODES}
        origin = {n: int(json.loads(start[n]["payload"])["uptime_ms"]) for n in NODES}
        dump(folder/"node-starts.json", start)
        result.update(experiment_id=experiment["id"], start_monotonic_ns=time.monotonic_ns(), boots=boots, origin_uptime_ms=origin)
        dump(folder/"result.json", result)
        pending = list(actions(scenario))
        clock_history = {n: [] for n in NODES}
        futures = {}
        busy = set()
        finished_nodes = set()
        wall_deadline = time.monotonic()+DURATIONS[scenario]*8+180
        event_log = (folder/"actions.jsonl").open("a", buffering=1)
        last_snapshot = 0
        outage_shot=False
        fault_shot=False
        while len(finished_nodes) != 3 or pending or futures:
            state = observer()
            if state["errors"]:
                raise RuntimeError(str(state["errors"]))
            if time.monotonic() > wall_deadline:
                raise RuntimeError("Finite wall timeout exceeded; no shortened run accepted")
            for node in NODES:
                serial = state["serial"].get(node)
                if not serial or time.monotonic_ns()-serial["monotonic_ns"] > 10e9:
                    raise RuntimeError("Serial observer stopped or node clock stale: "+node)
                telemetry = state["telemetry"].get(node)
                if telemetry and telemetry["payload"]["boot_id"] != boots[node]:
                    raise RuntimeError("Unexpected boot change: "+node)
            elapsed = {}
            for node in NODES:
                clock = state["serial"][node]
                points = clock_history[node]
                if not points or clock["uptime_ms"] > points[-1][0]:
                    points.append((clock["uptime_ms"], clock["monotonic_ns"]))
                    del points[:-10]
                rate = (points[-1][0]-points[0][0])/((points[-1][1]-points[0][1])/1e6) if len(points)>1 else .5
                elapsed[node] = (predicted_uptime(clock, rate, time.monotonic_ns())-origin[node])/1000
            if scenario=="EX-07" and elapsed["node_02"]>=70 and not outage_shot:
                snapshot=request("http://127.0.0.1:18773","/state")
                dump(folder/"dashboard-offline.json",snapshot)
                request("http://127.0.0.1:18773","/shot",dict(name=folder.name+'-broker-offline.png'))
                outage_shot=True
            if scenario=="EX-06" and elapsed["node_02"]>=75 and not fault_shot:
                snapshot=request("http://127.0.0.1:18773","/state")
                dump(folder/"dashboard-fault.json",snapshot)
                request("http://127.0.0.1:18773","/shot",dict(name=folder.name+'-open-load.png'))
                fault_shot=True
            for future in list(futures):
                if not future.done():
                    continue
                event = futures.pop(future)
                busy.remove(event.node_id)
                row = future.result()
                confirmation=row.get("physical_confirmation")
                upper=confirmation["uptime_ms"] if confirmation else max(row["before_clock"]["uptime_ms"], row["after_clock"]["uptime_ms"])+1000
                row["lateness_upper_node_ms"] = 0 if confirmation and confirmation.get("not_applicable") else upper-origin[event.node_id]-event.at_s*1000
                event_log.write(json.dumps(row)+"\n")
                result["actions"].append(row)
                if not event.kind.startswith("prepare-") and row["lateness_upper_node_ms"] > 2000:
                    raise RuntimeError(f"Action late beyond2s upper bound: {event} {row['lateness_upper_node_ms']}ms")
            for event in list(pending):
                if event.node_id in busy or elapsed[event.node_id] < event.at_s:
                    continue
                if elapsed[event.node_id] > event.at_s+2:
                    raise RuntimeError(f"Missed action; not replayed in burst: {event}")
                pending.remove(event)
                busy.add(event.node_id)
                futures[pool.submit(perform, config, event)] = event
            with database(config) as db:
                for node in NODES:
                    if node in finished_nodes:
                        continue
                    row = db.execute("SELECT * FROM telemetry WHERE node_id=? AND boot_id=? AND received_at>=? AND quality='ACCEPTED' AND length(uptime_ms)>=? ORDER BY received_at,id",
                                     (node, boots[node], start[node]["received_at"], len(str(origin[node]+DURATIONS[scenario]*1000)))).fetchall()
                    last = next((r for r in row if int(r["uptime_ms"]) >= origin[node]+DURATIONS[scenario]*1000), None)
                    if last:
                        result["windows"][node] = dict(first=start[node], last=dict(last),
                                                     duration_uptime_ms=int(last["uptime_ms"])-origin[node])
                        finished_nodes.add(node)
            if time.monotonic()-last_snapshot > 5:
                health = state.get("health", {})
                if health and health["value"].get("dropped_events", 0):
                    raise RuntimeError("Backend dropped events")
                if not health or time.monotonic_ns()-health["monotonic_ns"] > 10e9:
                    raise RuntimeError("HTTP health probe coverage lost")
                if scenario != "EX-07" and (not state["mqtt_connected"] or health["value"]["status"] != "OK"):
                    raise RuntimeError("Unexpected MQTT/collector outage")
                dump(folder/"result.json", result)
                dump(qa/"campaign-status.json", dict(status="RUNNING", current=str(folder), scenario=scenario,
                     repeat=repeat, elapsed_node_s=elapsed, completed_nodes=sorted(finished_nodes), pending_actions=len(pending)))
                last_snapshot = time.monotonic()
            time.sleep(.1)
        event_log.close()
        result["end_monotonic_ns"] = time.monotonic_ns()
        request("http://127.0.0.1:18773","/shot",dict(name=folder.name+'-dashboard-end.png'))
        result["status"] = "COLLECTED"
    except Exception as exc:
        result["status"] = "INCOMPLETE"
        result["errors"].append(str(exc))
        result["exception_traceback"] = traceback.format_exc()
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
        if scenario == "EX-07":
            try:
                health = request(config["api"], "/api/health")
            except HTTPError:
                owned_broker(config, "start")
            except Exception as exc:
                result["errors"].append("Broker restoration: "+str(exc))
        if experiment:
            try:
                stopped = request(config["api"], f"/api/experiments/{experiment['id']}/stop", {})
                dump(folder/"experiment-stop.json", stopped)
                export = request(config["api"], f"/api/experiments/{experiment['id']}/export.csv")
                (folder/"export.csv").write_text(export)
            except Exception as exc:
                result["status"] = "INCOMPLETE"
                result["errors"].append("Stop/export: "+str(exc))
        dump(folder/"result.json", result)
        dump(qa/"campaign-status.json", dict(status=result["status"], current=str(folder), errors=result["errors"]))
    return folder, result


def in_recording_window(event, result):
    """Monotonic values are comparable only inside the same host boot cohort.

    Historic untagged recordings remain a separate cohort and are never mixed
    with newly tagged data, even if their monotonic ranges happen to overlap.
    """
    return (event.get("host_boot_id") == result.get("host_boot_id") and
            result["start_monotonic_ns"] <= event["monotonic_ns"] <= result["end_monotonic_ns"])


def audit_behavior(config, result):
    """Validate physical outcomes against independent raw streams, not UI success alone."""
    qa = Path(config["qa"])
    def read(name):
        values=[]
        with (qa/(name+".jsonl")).open() as stream:
            for line in stream:
                value=json.loads(line)
                if in_recording_window(value, result):
                    values.append(value)
        return values
    mqtt = read("mqtt-events")
    serial = read("serial-events")
    probes = read("probe-events")
    telemetry = {node:[e for e in mqtt if e.get("topic", "").endswith('/'+node+'/telemetry')] for node in NODES}
    errors=[]
    proof=[]
    for node, values in telemetry.items():
        if not values or any(v["payload"]["boot_id"] != result["boots"][node] or v["payload"]["mode"] != "AUTO" for v in values):
            errors.append(dict(node_id=node,error="Missing AUTO stream or changed boot"))
    if any(e.get("topic", "").endswith("/command") for e in mqtt):
        errors.append(dict(error="Unexpected command inside measurement"))
    if any(e.get("event")=="health" and e["value"].get("dropped_events", 0) for e in probes):
        errors.append(dict(error="Dropped events observed"))
    if result["scenario"] != "EX-07" and any(e["event"] in ("connected","disconnected") for e in mqtt):
        errors.append(dict(error="Unexpected recorder reconnect"))
    distances={n:scene(result["scenario"],n)["distance"] for n in NODES}
    environments={n:scene(result["scenario"],n)["environment"] for n in NODES}
    for action in sorted(result["actions"],key=lambda a:a["started_host_ms"]):
        event=action["recipe"];node=event["node_id"];kind=event["kind"]
        if kind=="scene":
            distances[node]=event["value"]["distance"]
            environments[node]=event["value"]["environment"]
        elif kind=="distance":
            distances[node]=event["value"]
        elif kind=="motion":
            expected_motion="VEHICLE" if distances[node]<100 else "PEDESTRIAN"
            expected_target=0 if environments[node]=="DAY" else 100 if expected_motion=="VEHICLE" else 70
            lower=action["before_clock"]["uptime_ms"]-1000
            matches=[v for v in telemetry[node] if lower <= v["payload"]["uptime_ms"] <= lower+9000 and
                     v["host_ms"] >= action["started_host_ms"] and v["payload"]["motion"]==expected_motion and
                     v["payload"]["brightness_target"]==expected_target]
            if not matches:
                errors.append(dict(node_id=node,at_s=event["at_s"],error="Missing PIR classification/target",expected_motion=expected_motion,expected_target=expected_target))
            else:
                proof.append(dict(node_id=node,at_s=event["at_s"],kind="motion",seq=matches[0]["payload"]["seq"],motion=expected_motion,target=expected_target))
    if result["scenario"] in ("PILOT","EX-06"):
        targets=NODES if result["scenario"]=="PILOT" else ("node_02",)
        for node in targets:
            faults=[e for e in telemetry[node] if "OPEN_LOAD" in e["payload"]["faults"]]
            clear=[e for e in telemetry[node] if faults and e["host_ms"]>faults[-1]["host_ms"] and not e["payload"]["faults"] and e["payload"]["current_adc"]>=3891]
            if not faults or not clear:
                errors.append(dict(node_id=node,error="OPEN_LOAD/recovery not observed"))
            else:
                proof.append(dict(node_id=node,kind="OPEN_LOAD/recovery",fault_seq=faults[0]["payload"]["seq"],clear_seq=clear[0]["payload"]["seq"]))
        if result["scenario"]=="EX-06" and any(e["payload"]["faults"] for n in ("node_01","node_03") for e in telemetry[n]):
            errors.append(dict(error="Fault propagated to another node"))
    if result["scenario"]=="EX-02":
        for node, values in telemetry.items():
            if any(e["payload"]["brightness_target"] != 25 or e["payload"]["brightness_applied"] != 25 or e["payload"]["faults"] or e["payload"]["motion"] != "NONE" for e in values):
                errors.append(dict(node_id=node,error="Quiet NIGHT25 not maintained"))
    if result["scenario"]=="EX-01":
        for node,values in telemetry.items():
            if any(e["payload"]["environment"]!="DAY" or e["payload"]["brightness_target"]!=0 or e["payload"]["brightness_applied"]!=0 for e in values):
                errors.append(dict(node_id=node,error="DAY0 changed during motion"))
    if result["scenario"]=="EX-05":
        for node,values in telemetry.items():
            for phase in range(3):
                expected=scene("EX-05",node,phase)["environment"]
                points=[e for e in values if phase*300+8 <= (e["payload"]["uptime_ms"]-result["origin_uptime_ms"][node])/1000 < (phase+1)*300]
                if not points or any(e["payload"]["environment"]!=expected for e in points):
                    errors.append(dict(node_id=node,phase=phase,error="Mixed environment phase missing or incorrect",expected=expected))
                else:
                    proof.append(dict(node_id=node,phase=phase,kind="environment",expected=expected,samples=len(points)))
    if result["scenario"]=="EX-07":
        stopped=next(a for a in result["actions"] if a["recipe"]["kind"]=="broker" and a["recipe"]["value"]=="stop")
        restarted=next(a for a in result["actions"] if a["recipe"]["kind"]=="broker" and a["recipe"]["value"]=="start")
        offline=[e for e in serial if stopped["finished_host_ms"]<=e["host_ms"]<=restarted["started_host_ms"]]
        for node in NODES:
            lines=[e for e in offline if e.get("node_id")==node and e["line"].startswith("CONTROL ") and "mode=AUTO" in e["line"] and "mqtt=0" in e["line"]]
            if not lines:
                errors.append(dict(node_id=node,error="Missing AUTO offline Serial proof"))
            else:
                proof.append(dict(node_id=node,kind="AUTO offline",serial=lines[0]))
        node1=[e["line"] for e in offline if e.get("node_id")=="node_01"]
        if not any("environment=DAY" in l and "target=0 " in l for l in node1) or not any("environment=NIGHT" in l and "target=25 " in l for l in node1):
            errors.append(dict(error="Missing node01 sensor response while broker offline"))
        if not any(e["event"]=="health" and not e["value"]["broker"] for e in probes):
            errors.append(dict(error="Missing degraded API health"))
    return dict(status="PASS" if not errors else "FAIL",proof=proof,errors=errors,
                raw_event_counts=dict(mqtt=len(mqtt),serial=len(serial),probes=len(probes)))


def summarize_attempt(config, folder):
    result = json.loads((folder/"result.json").read_text())
    if result["status"] not in ("COLLECTED", "PASS"):
        return result
    errors = []
    behavior = audit_behavior(config, result)
    errors += behavior["errors"]
    dump(folder/"behavior-audit.json", behavior)
    analyses = {}
    csv_rows = list(csv.DictReader(io.StringIO((folder/"export.csv").read_text())))
    with database(config) as db:
        for node, window in result["windows"].items():
            # HTTP timestamps have microsecond precision; enclose the chosen SQL rows
            # instead of rounding a boundary inwards and silently losing an endpoint.
            def utc(value):
                return datetime.fromtimestamp(value, timezone.utc).isoformat().replace("+00:00", "Z")
            from_utc=utc(window["first"]["received_at"]-.000002)
            to_utc=utc(window["last"]["received_at"]+.000002)
            start=datetime.fromisoformat(from_utc.replace("Z","+00:00")).timestamp()
            end=datetime.fromisoformat(to_utc.replace("Z","+00:00")).timestamp()
            rows = db.execute("SELECT * FROM telemetry WHERE node_id=? AND received_at>=? AND received_at<=? ORDER BY received_at,id", (node, start, end)).fetchall()
            independent, segments = calculate(rows, end-start)
            query = urlencode(dict(node_id=node, experiment_id=result["experiment_id"], **{"from": from_utc, "to": to_utc}))
            api = request(config["api"], "/api/stats?"+query)
            errors += [dict(node_id=node, **item) for item in compare_stats(independent, api["nodes"][0])]
            expected_seq = [int(r["seq"]) for r in rows if r["quality"] == "ACCEPTED"]
            if result["scenario"] != "EX-07" and any(b != a+1 for a,b in zip(expected_seq, expected_seq[1:])):
                errors.append(dict(node_id=node, error="Unexpected sequence gap"))
            selected = [r for r in csv_rows if r["node_id"] == node and start <= datetime.fromisoformat(r["received_at"].replace("Z", "+00:00")).timestamp() <= end]
            # CSV begins at the common experiment start. Recompute the per-node first boundary.
            for field in ("total_energy_wh", "auto_energy_wh", "baseline_wh"):
                value = sum(float(r[field]) for r in selected[1:])
                if abs(value-independent[field]) > 1e-9:
                    errors.append(dict(node_id=node, field="CSV "+field, independent=independent[field], csv=value))
            analyses[node] = dict(independent=independent, api=api, segment_count=len(segments),
                                  first_seq=expected_seq[0], last_seq=expected_seq[-1],
                                  duration_uptime_ms=window["duration_uptime_ms"],from_utc=from_utc,to_utc=to_utc,
                                  timestamp_boundary_policy="Enclose selected SQL endpoints by2 microseconds before UTC serialization")
    dump(folder/"analysis.json", dict(status="PASS" if not errors else "FAIL", nodes=analyses, errors=errors))
    result["status"] = "PASS" if not errors else "FAIL"
    result["errors"] += errors
    dump(folder/"result.json", result)
    return result
