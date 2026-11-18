"""Frozen SRS9.3 recipes. All event times are relative node uptime seconds."""

from dataclasses import asdict, dataclass

NODES = ("node_01", "node_02", "node_03")
DURATIONS = {"PILOT": 90, "EX-01": 300, "EX-02": 600, "EX-03": 600,
             "EX-04": 600, "EX-05": 900, "EX-06": 300, "EX-07": 300}
REPEATS = {key: 3 if key in ("EX-02", "EX-03", "EX-04", "EX-05") else 1
           for key in DURATIONS if key != "PILOT"}


@dataclass(frozen=True)
class Action:
    at_s: int
    node_id: str
    kind: str
    value: object = None


def scene(scenario, node, phase=0):
    """Physical input recipe, never a target PWM or injected telemetry."""
    index = NODES.index(node)
    if scenario == "EX-01":
        return {"environment": "DAY", "distance": 150}
    if scenario == "EX-05":
        environments = (("DAY", "NIGHT", "NIGHT"),
                        ("TWILIGHT", "NIGHT", "NIGHT"),
                        ("NIGHT", "DAY", "NIGHT"))
        distances = ((150, 150, 150), (150, 150, 50), (50, 150, 150))
        return {"environment": environments[phase][index], "distance": distances[phase][index]}
    return {"environment": "NIGHT", "distance": 50 if scenario == "EX-04" else 150}


def actions(scenario):
    if scenario not in DURATIONS:
        raise ValueError("Unknown scenario")
    result = []
    for node in NODES:
        if scenario == "PILOT":
            result += [Action(15, node, "motion"), Action(35, node, "prepare-distance", 50), Action(40, node, "distance", 50),
                       Action(45, node, "motion"), Action(60, node, "current", 0),
                       Action(75, node, "current", 1023)]
        elif scenario == "EX-01":
            for index, at in enumerate(range(15, 300, 30)):
                result += [Action(at - 10, node, "prepare-distance", 150 if index % 2 == 0 else 50),
                           Action(at - 5, node, "distance", 150 if index % 2 == 0 else 50),
                           Action(at, node, "motion")]
        elif scenario in ("EX-03", "EX-04"):
            result += [Action(at, node, "motion") for at in range(15, 600, 30)]
        elif scenario == "EX-05":
            result += [Action(290, node, "prepare-scene", scene(scenario, node, 1)),
                       Action(300, node, "scene", scene(scenario, node, 1)),
                       Action(590, node, "prepare-scene", scene(scenario, node, 2)),
                       Action(600, node, "scene", scene(scenario, node, 2))]
            active = {"node_01": (2,), "node_02": (1,), "node_03": (0, 1)}
            for phase in active[node]:
                result += [Action(at, node, "motion") for at in range(phase * 300 + 15, (phase + 1) * 300, 30)]
    if scenario == "EX-06":
        result += [Action(60, "node_02", "current", 0), Action(180, "node_02", "current", 1023)]
    elif scenario == "EX-07":
        # Shared broker operations intentionally use node02 as the reference clock.
        result += [Action(60, "node_02", "broker", "stop"),
                   Action(75, "node_02", "offline_ldr", "DAY"),
                   Action(90, "node_02", "offline_ldr", "NIGHT"),
                   Action(120, "node_02", "broker", "start")]
    return sorted(result, key=lambda item: (item.at_s, item.node_id, item.kind))


def configuration(scenario, repeat):
    if repeat < 1 or repeat > (1 if scenario == "PILOT" else REPEATS[scenario]):
        raise ValueError("Repeat outside frozen schedule")
    return {"source": "Wokwi live", "scenario": scenario, "repeat": repeat,
            "duration_node_s": DURATIONS[scenario], "clock_basis": "per_node_uptime",
            "energy_clock": "node_uptime", "coverage_clock": "receiver_utc",
            "action_max_lateness_node_ms": 2000, "pilot": scenario == "PILOT",
            "initial_scenes": {node: scene(scenario, node) for node in NODES},
            "actions": [asdict(item) for item in actions(scenario)]}


def campaign():
    return [(scenario, repeat) for scenario, count in REPEATS.items() for repeat in range(1, count + 1)]
