#!/usr/bin/env python3
"""Audit frozen live attempts against raw MQTT and SQLite without changing them."""

import argparse
import csv
from collections import Counter, defaultdict
import datetime
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import statistics
import sys

from experiment_tools.analysis import calculate, compare_stats
from experiment_tools.recipes import NODES, campaign, configuration
from experiment_tools.integrity import compare_csv


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    root = args.run_dir.resolve()
    runtime = read(root / "runtime.json")
    attempts = []
    accepted = {}
    errors = []
    for path in sorted((root / "attempts").glob("*/result.json")):
        result = read(path)
        if result["scenario"] == "PILOT":
            continue
        item = {key: result[key] for key in ("scenario", "repeat", "attempt", "status", "errors")}
        item["folder"] = path.parent.name
        attempts.append(item)
        key = (result["scenario"], result["repeat"])
        if result["status"] == "PASS":
            if result["configuration"] != configuration(*key):
                errors.append({"attempt": path.parent.name, "error": "Recipe differs from approved configuration"})
            elif key in accepted:
                errors.append({"attempt": path.parent.name, "error": "Multiple valid repetitions; do not select a favorable result"})
            else:
                accepted[key] = (path.parent, result)
    # Only inspect the complete JSONL prefix observed by this invocation. A live writer
    # may append later; a partial trailing line is not part of this snapshot.
    raw = defaultdict(list)
    raw_path = root / "mqtt-events.jsonl"
    digest = hashlib.sha256()
    raw_bytes = 0
    with raw_path.open("rb") as stream:
        for line in stream:
            if not line.endswith(b"\n"):
                break
            digest.update(line)
            raw_bytes += len(line)
            event = json.loads(line)
            payload = event.get("payload")
            if event.get("event") != "message" or not event.get("topic", "").endswith("/telemetry") or not isinstance(payload, dict):
                continue
            key = (payload["node_id"], payload["boot_id"], str(payload["seq"]))
            raw[key].append(payload)
    connection = sqlite3.connect(f"file:{runtime['database']}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("BEGIN")
    runs = []
    metrics = defaultdict(list)
    for key in campaign():
        if key not in accepted:
            continue
        folder, result = accepted[key]
        original = read(folder / "analysis.json")
        with (folder / "export.csv").open(newline="") as stream:
            exported = list(csv.DictReader(stream))
        run = {"scenario": key[0], "repeat": key[1], "attempt": folder.name,
               "experiment_id": result["experiment_id"], "nodes": {}, "errors": []}
        if set(result["windows"]) != set(NODES):
            run["errors"].append({"error": "Per-node windows do not include exactly3 approved node IDs"})
        physical = [row for row in result["actions"] if not row["recipe"]["kind"].startswith("prepare-")]
        scheduled = [row for row in result["configuration"]["actions"] if not row["kind"].startswith("prepare-")]
        canonical = lambda row: json.dumps(row, sort_keys=True, separators=(",", ":"))
        if Counter(canonical(row["recipe"]) for row in physical) != Counter(canonical(row) for row in scheduled):
            run["errors"].append({"error": "Physical action list differs from frozen recipe"})
        offsets = [row.get("lateness_upper_node_ms") for row in physical]
        if any(not isinstance(value, (int,float)) or not math.isfinite(value) or value > 2000 for value in offsets):
            run["errors"].append({"error": "Physical action lateness missing or exceeds2 simulated seconds"})
        numeric_offsets = [value for value in offsets if isinstance(value, (int,float)) and math.isfinite(value)]
        run["action_summary"] = dict(physical_actions=len(physical),
                                     minimum_offset_ms=min(numeric_offsets) if numeric_offsets else None,
                                     maximum_lateness_upper_ms=max(numeric_offsets) if numeric_offsets else None,
                                     upper_limit_ms=2000)
        for node_id, window in sorted(result["windows"].items()):
            first, last = window["first"], window["last"]
            rows = connection.execute("SELECT * FROM telemetry WHERE node_id=? AND id>=? AND id<=? ORDER BY id", (node_id, first["id"], last["id"])).fetchall()
            api = original["nodes"][node_id]["api"]["nodes"][0]
            # The stored query boundaries are serialized UTC. Reuse their actual
            # elapsed interval to avoid treating sub-microsecond float rounding as
            # an energy disagreement.
            from_time = datetime.datetime.fromisoformat(original["nodes"][node_id]["from_utc"].replace("Z", "+00:00")).timestamp()
            to_time = datetime.datetime.fromisoformat(original["nodes"][node_id]["to_utc"].replace("Z", "+00:00")).timestamp()
            expected, _ = calculate(rows, to_time - from_time)
            comparisons = compare_stats(expected, api)
            selected_csv = [row for row in exported if row["node_id"] == node_id and
                            from_time <= datetime.datetime.fromisoformat(row["received_at"].replace("Z", "+00:00")).timestamp() <= to_time]
            csv_errors = compare_csv(rows, selected_csv, expected)
            missing = []
            mismatched = []
            payload_hash = hashlib.sha256()
            sequences = []
            for row in rows:
                payload = json.loads(row["payload"])
                row_key = (node_id, payload["boot_id"], str(payload["seq"]))
                matches = raw.get(row_key, [])
                if not matches:
                    missing.append(str(payload["seq"]))
                elif not any(item == payload for item in matches):
                    mismatched.append(str(payload["seq"]))
                payload_hash.update((json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())
                sequences.append(int(payload["seq"]))
            absent_sql = []
            sql_sequences = set(sequences)
            for (raw_node, boot, seq), values in raw.items():
                if raw_node == node_id and boot == first["boot_id"] and sequences[0] <= int(seq) <= sequences[-1] and int(seq) not in sql_sequences:
                    absent_sql.append(seq)
            duration = (int(last["uptime_ms"]) - int(first["uptime_ms"])) / 1000
            node = dict(expected, duration_uptime_s=duration, boot_id=first["boot_id"],
                        from_utc=original["nodes"][node_id]["from_utc"], to_utc=original["nodes"][node_id]["to_utc"],
                        first_seq=str(sequences[0]), last_seq=str(sequences[-1]),
                        raw_sql_payload_sha256=payload_hash.hexdigest(), raw_missing=missing, payload_mismatch=mismatched,
                        raw_not_in_sql=absent_sql, independent_api_errors=comparisons,
                        independent_csv_errors=csv_errors,
                        sequence_gaps=sum(max(0, right-left-1) for left,right in zip(sequences,sequences[1:])))
            run["nodes"][node_id] = node
            if missing or mismatched or absent_sql or comparisons or csv_errors or any(row["quality"] != "ACCEPTED" for row in rows):
                run["errors"].append({"node_id": node_id, "error": "Raw/SQL/API comparison failed"})
            if duration < configuration(*key)["duration_node_s"]:
                run["errors"].append({"node_id": node_id, "error": "Duration shorter than approved recipe"})
            if any(row["boot_id"] != first["boot_id"] for row in rows):
                run["errors"].append({"node_id": node_id, "error": "Unexpected boot change in accepted window"})
            if key[0] != "EX-07" and node["sequence_gaps"]:
                run["errors"].append({"node_id": node_id, "error": "Unexpected sequence gap outside broker-outage scenario"})
            metrics[key[0]].append(node)
        run["status"] = "PASS" if not run["errors"] else "FAIL"
        errors.extend({"attempt": folder.name, **item} for item in run["errors"])
        runs.append(run)
    integrity = connection.execute("PRAGMA quick_check").fetchall()
    connection.rollback()
    connection.close()
    if [row[0] for row in integrity] != ["ok"]:
        errors.append({"error": "SQLite quick_check failed"})
    missing = [dict(scenario=scenario, repeat=repeat) for scenario,repeat in campaign() if (scenario,repeat) not in accepted]
    aggregates = {}
    for scenario, values in metrics.items():
        fields = {}
        for field in ("auto_energy_wh", "baseline_wh", "saving_percent", "average_auto_power_w", "auto_valid_uptime_s", "coverage_percent"):
            data = [item[field] for item in values if item[field] is not None]
            fields[field] = dict(mean=statistics.mean(data), minimum=min(data), maximum=max(data), n=len(data)) if data else None
        aggregates[scenario] = dict(node_run_observations=len(values), fields=fields)
    output = dict(status="FAIL" if errors else "INCOMPLETE" if missing else "PASS",
                  generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  accepted_runs=len(runs), planned_runs=15, attempts=attempts, missing=missing,
                  raw_snapshot_bytes=raw_bytes, raw_snapshot_sha256=digest.hexdigest(),
                  sqlite_quick_check=[row[0] for row in integrity], runs=runs, aggregates=aggregates, errors=errors,
                  aggregation_note="Descriptive node-run observations; not independent real-world subjects. Report repetition totals separately.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in ("status", "accepted_runs", "missing", "errors")}))
    return int(bool(errors) or (args.require_complete and bool(missing)))


if __name__ == "__main__":
    sys.exit(main())
