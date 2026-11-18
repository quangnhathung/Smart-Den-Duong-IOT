#!/usr/bin/env python3
"""Export descriptive repetition metrics and publication figures from an audit."""

import argparse
import csv
import json
import hashlib
import os
from pathlib import Path
import statistics
import tempfile

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="task012-mpl-"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    audit = json.loads(args.audit.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    observations = []
    repetitions = []
    for run in audit["runs"]:
        for node_id, node in run["nodes"].items():
            observations.append(dict(scenario=run["scenario"], repeat=run["repeat"], experiment_id=run.get("experiment_id"),
                                     node_id=node_id, boot_id=node.get("boot_id"), from_utc=node.get("from_utc"), to_utc=node.get("to_utc"),
                                     **{key: node[key] for key in ("total_energy_wh", "auto_energy_wh", "baseline_wh", "saving_percent", "valid_uptime_s", "auto_valid_uptime_s", "average_auto_power_w", "coverage_percent", "covered_wall_s", "missing_wall_s", "sample_count", "duration_uptime_s")}))
        nodes = list(run["nodes"].values())
        energy = sum(node["auto_energy_wh"] for node in nodes)
        baseline = sum(node["baseline_wh"] for node in nodes)
        duration = sum(node["auto_valid_uptime_s"] for node in nodes)
        repetitions.append(dict(scenario=run["scenario"], repeat=run["repeat"], auto_energy_wh=energy,
                                baseline_wh=baseline, average_auto_power_w=energy * 3600 / duration if duration else None,
                                average_baseline_power_w=baseline * 3600 / duration if duration else None,
                                saving_percent=100 * (baseline-energy)/baseline if baseline else None,
                                coverage_min_percent=min(node["coverage_percent"] for node in nodes)))
    for name, rows in [("node-metrics.csv", observations), ("repetition-metrics.csv", repetitions)]:
        if rows:
            with (args.output / name).open("w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    variation = []
    for scenario in sorted({row["scenario"] for row in repetitions}):
        values = [row for row in repetitions if row["scenario"] == scenario]
        item = dict(scenario=scenario, repetitions=len(values))
        for field in ("average_auto_power_w", "average_baseline_power_w", "saving_percent", "coverage_min_percent"):
            samples = [row[field] for row in values if row[field] is not None]
            item[field] = dict(mean=statistics.mean(samples), minimum=min(samples), maximum=max(samples)) if samples else None
        variation.append(item)
    (args.output / "variation.json").write_text(json.dumps(variation, indent=2, ensure_ascii=False) + "\n")
    (args.output / "plot-source.json").write_text(json.dumps(dict(audit_sha256=hashlib.sha256(args.audit.read_bytes()).hexdigest(), accepted_runs=audit["accepted_runs"]), indent=2) + "\n")
    eligible = [row for row in variation if row["scenario"] in ("EX-01", "EX-02", "EX-03", "EX-04", "EX-05")]
    if eligible:
        plt.rcParams.update({"font.family": "Arial", "font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
        figure, axis = plt.subplots(figsize=(9.6, 4.6), layout="constrained")
        x = list(range(len(eligible)))
        means = [row["average_auto_power_w"]["mean"] for row in eligible]
        low = [mean-row["average_auto_power_w"]["minimum"] for mean,row in zip(means,eligible)]
        high = [row["average_auto_power_w"]["maximum"]-mean for mean,row in zip(means,eligible)]
        axis.bar([value-.18 for value in x], means, width=.36, color="#237A4B", label="AUTO mô phỏng", yerr=[low,high], capsize=4)
        axis.bar([value+.18 for value in x], [row["average_baseline_power_w"]["mean"] for row in eligible], width=.36, color="#475569", label="Baseline cùng đoạn")
        axis.set_xticks(x, [row["scenario"] + f"\n(n={row['repetitions']})" for row in eligible])
        axis.set_ylabel("Công suất trung bình trên thời gian AUTO hợp lệ (W/node)")
        axis.set_ylim(0, 28)
        axis.set_title("Mô hình Wokwi — trung bình và min–max giữa các lần lặp", pad=16)
        axis.grid(axis="y", color="#E2E8F0", zorder=0)
        axis.set_axisbelow(True)
        axis.legend(frameon=False, ncol=2)
        figure.savefig(args.output / "auto-power-repetitions.png", dpi=200)
        plt.close(figure)
    print(json.dumps(dict(node_observations=len(observations), repetitions=len(repetitions), output=str(args.output))))


if __name__ == "__main__":
    main()
