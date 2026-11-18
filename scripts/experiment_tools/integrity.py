"""Read-only checks for exported rows; separate from the live producer."""

import json
import math


def compare_csv(rows, exported, expected):
    errors = []
    if len(rows) != len(exported):
        return [dict(field="CSV sample_count", sql=len(rows), csv=len(exported))]
    for source, record in zip(rows, exported):
        payload = json.loads(source["payload"])
        for field, value in payload.items():
            actual = record.get(field)
            equal = False
            try:
                if value is None:
                    equal = actual == ""
                elif isinstance(value, list):
                    equal = json.loads(actual) == value
                elif isinstance(value, (int, float)):
                    # Integers may occupy the full uint64 range: never compare
                    # seq/uptime through float and lose their low bits.
                    equal = int(actual) == value if isinstance(value, int) else math.isfinite(float(actual)) and float(actual) == value
                else:
                    equal = actual == value
            except (ValueError, TypeError, json.JSONDecodeError):
                pass
            if not equal:
                errors.append(dict(field="CSV payload "+field, seq=str(payload["seq"]), sql=value, csv=actual))
        for field in ("quality", "continuity"):
            if record.get(field) != source[field]:
                errors.append(dict(field="CSV "+field, seq=str(payload["seq"])))
    for field in ("total_energy_wh", "auto_energy_wh", "baseline_wh"):
        try:
            # The first chosen CSV row may refer to an earlier segment outside
            # this node's selected window. It must not contribute energy.
            values = [float(row[field]) for row in exported[1:]]
            actual = sum(values)
            valid = all(math.isfinite(value) for value in values) and abs(actual-expected[field]) <= 1e-9
        except (ValueError, KeyError, TypeError):
            actual, valid = None, False
        if not valid:
            errors.append(dict(field="CSV "+field, independent=expected[field], csv=actual))
    return errors
