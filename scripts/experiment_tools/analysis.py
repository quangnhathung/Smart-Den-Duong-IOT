"""Independent SRS energy calculation from frozen SQLite payloads, not API totals."""

import json
import math
from collections import Counter


def calculate(rows, elapsed_wall_s):
    totals = dict(total_energy_wh=0.0, auto_energy_wh=0.0, baseline_wh=0.0,
                  valid_uptime_s=0.0, auto_valid_uptime_s=0.0, covered_wall_s=0.0)
    previous = None
    details = []
    excluded = Counter()
    for source in rows:
        row = dict(source)
        data = json.loads(row["payload"])
        reasons = []
        dt = covered = energy = auto_energy = baseline = 0.0
        if previous is None:
            reasons = ["FIRST_SAMPLE"]
        else:
            left_row, left = previous
            delta = (int(data["uptime_ms"]) - int(left["uptime_ms"])) / 1000
            if left_row["quality"] != "ACCEPTED" or row["quality"] != "ACCEPTED":
                reasons.append("QUALITY")
            if left["boot_id"] != data["boot_id"]:
                reasons.append("BOOT_CHANGE")
            if left_row["continuity"] != row["continuity"]:
                reasons.append("DISCONTINUITY")
            if int(data["seq"]) <= int(left["seq"]) or not 0 < delta <= 6:
                reasons.append("ORDER_OR_GAP")
            if row["received_at"] <= left_row["received_at"]:
                reasons.append("RECEIVE_CLOCK_ORDER")
            if not reasons:
                dt = delta
                covered = row["received_at"] - left_row["received_at"]
                energy = (float(left["power_sim_w"]) + float(data["power_sim_w"])) * delta / 7200
                if left["mode"] != "AUTO" or data["mode"] != "AUTO":
                    reasons.append("MANUAL")
                if left["faults"] or data["faults"]:
                    reasons.append("FAULT_OR_RECOVERY")
                if min(left["current_adc"], data["current_adc"]) < 4095 * .95:
                    reasons.append("LOAD_CALIBRATION_OR_FAULT_CONFIRMATION")
                if "UNKNOWN" in (left["environment"], data["environment"]):
                    reasons.append("UNKNOWN_ENVIRONMENT")
                if any(left[k] != data[k] for k in ("environment", "mode", "faults")):
                    reasons.append("STATE_CHANGE")
                if not reasons:
                    auto_energy = energy
                    baseline = (0 if data["environment"] == "DAY" else 24) * delta / 3600
        totals["total_energy_wh"] += energy
        totals["auto_energy_wh"] += auto_energy
        totals["baseline_wh"] += baseline
        totals["valid_uptime_s"] += dt
        totals["auto_valid_uptime_s"] += dt if not reasons else 0
        totals["covered_wall_s"] += covered
        excluded.update(reasons)
        details.append(dict(seq=str(data["seq"]), uptime_ms=str(data["uptime_ms"]),
                            total_energy_wh=energy, auto_energy_wh=auto_energy,
                            baseline_wh=baseline, valid_uptime_s=dt, covered_wall_s=covered,
                            auto_eligible=previous is not None and not reasons, excluded_reasons=reasons))
        previous = row, data
    totals["covered_wall_s"] = min(elapsed_wall_s, totals["covered_wall_s"])
    totals.update(missing_wall_s=max(0, elapsed_wall_s-totals["covered_wall_s"]),
                  coverage_percent=100*totals["covered_wall_s"]/elapsed_wall_s if elapsed_wall_s else None,
                  saving_percent=100*(totals["baseline_wh"]-totals["auto_energy_wh"])/totals["baseline_wh"] if totals["baseline_wh"] else None,
                  average_auto_power_w=totals["auto_energy_wh"]*3600/totals["auto_valid_uptime_s"] if totals["auto_valid_uptime_s"] else None,
                  sample_count=len(details), excluded_intervals=dict(excluded))
    return totals, details


def compare_stats(expected, actual):
    errors = []
    for key in ("total_energy_wh", "auto_energy_wh", "baseline_wh", "valid_uptime_s",
                "auto_valid_uptime_s", "covered_wall_s", "missing_wall_s", "coverage_percent", "saving_percent"):
        left, right = expected[key], actual[key]
        if left is None or right is None:
            equal = left is right
        else:
            equal = math.isfinite(left) and math.isfinite(right) and abs(left-right) <= 1e-9
        if not equal:
            errors.append(dict(field=key, independent=left, api=right))
    if expected["sample_count"] != actual["sample_count"] or expected["excluded_intervals"] != actual["excluded_intervals"]:
        errors.append(dict(field="sample_count/excluded_intervals", independent=expected, api=actual))
    return errors
