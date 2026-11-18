#!/usr/bin/env python3
"""TASK-012 live experiment CLI. Never accepts synthetic data as a live run."""

import argparse
import json
from pathlib import Path
import signal
import sys

from experiment_tools.recipes import DURATIONS, campaign, configuration


def main():
    def interrupted(signum, _frame):
        raise RuntimeError(f"Experiment process interrupted by signal {signum}; retain attempt, never resume a partial window")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("preflight", "run", "summarize", "verify", "plan"))
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--scenario", choices=tuple(DURATIONS), default="PILOT")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--resume", action="store_true", help="Skip only complete PASS attempts with the exact frozen recipe; never resume a partial window")
    args = parser.parse_args()
    if args.operation == "plan":
        print(json.dumps([configuration(s, r) for s,r in campaign()] if args.all else configuration(args.scenario,args.repeat), indent=2))
        return 0
    if not args.run_dir:
        parser.error("--run-dir is required for this operation")
    from experiment_tools.live import collect_attempt, dump, preflight, summarize_attempt
    config = json.loads((args.run_dir/"runtime.json").read_text())
    if args.operation == "preflight":
        value = preflight(config)
        dump(args.run_dir/"preflight.json", value)
        print(json.dumps(value))
        return 0
    if args.operation == "run":
        for scenario, repeat in campaign() if args.all else [(args.scenario,args.repeat)]:
            if args.resume:
                accepted=[]
                for path in sorted((args.run_dir/"attempts").glob(f"{scenario}-r{repeat:02}-a*/result.json")):
                    previous=json.loads(path.read_text())
                    if previous["status"]=="PASS" and previous["configuration"]==configuration(scenario,repeat):
                        accepted.append(path)
                if accepted:
                    print(json.dumps(dict(scenario=scenario,repeat=repeat,reused_pass=str(accepted[-1]))),flush=True)
                    continue
            folder,result = collect_attempt(config,scenario,repeat)
            if result["status"] == "COLLECTED":
                result = summarize_attempt(config,folder)
            dump(args.run_dir/"campaign-status.json",dict(status=result["status"],current=str(folder),scenario=scenario,repeat=repeat,errors=result["errors"]))
            print(json.dumps(dict(attempt=str(folder),status=result["status"],errors=result["errors"])),flush=True)
            if result["status"] != "PASS":
                return 1
        if args.all:
            dump(args.run_dir/"campaign-completed.json",dict(status="COLLECTED",main_runs=15,clock_basis="per_node_uptime",next="verify all frozen evidence before handover"))
        return 0
    values=[]
    for folder in sorted((args.run_dir/"attempts").glob("*")):
        result=summarize_attempt(config,folder) if args.operation=="summarize" else json.loads((folder/"result.json").read_text())
        values.append(dict(scenario=result["scenario"],repeat=result["repeat"],status=result["status"],folder=str(folder)))
    missing=[(s,r) for s,r in campaign() if not any(v["scenario"]==s and v["repeat"]==r and v["status"]=="PASS" for v in values)]
    value=dict(status="PASS" if not missing else "INCOMPLETE",attempts=values,missing=missing)
    dump(args.run_dir/"campaign-summary.json",value)
    print(json.dumps(value))
    return int(bool(missing))


if __name__ == "__main__":
    sys.exit(main())
