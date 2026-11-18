"""Fixture checks for experiment safety and arithmetic; these are not live PASS."""

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from experiment_tools.analysis import calculate, compare_stats
from experiment_tools.recipes import NODES, actions, campaign, configuration, scene
from experiment_tools.live import in_recording_window, predicted_uptime
from experiment_tools.integrity import compare_csv


def row(seq=0, uptime=0, received=0, **changes):
    payload = dict(node_id="node_01", boot_id="12345678", seq=seq, uptime_ms=uptime,
                   power_sim_w=6, mode="AUTO", environment="NIGHT", faults=[], current_adc=4095)
    payload.update(changes)
    return dict(payload=json.dumps(payload), quality="ACCEPTED", continuity="session1", seq=str(seq),
                uptime_ms=str(uptime), received_at=received)


class RecipeChecks(unittest.TestCase):
    def test_reboot_does_not_mix_equal_monotonic_ranges(self):
        records=[dict(monotonic_ns=150,label='historic'),
                 dict(monotonic_ns=150,host_boot_id='boot-A',label='first'),
                 dict(monotonic_ns=150,host_boot_id='boot-B',label='second'),
                 dict(monotonic_ns=250,host_boot_id='boot-B',label='outside')]
        for boot,label in [(None,'historic'),('boot-A','first'),('boot-B','second')]:
            window=dict(start_monotonic_ns=100,end_monotonic_ns=200)
            if boot is not None:window['host_boot_id']=boot
            self.assertEqual([r['label'] for r in records if in_recording_window(r,window)],[label])

    def test_fifteen_main_runs_and_150_node_minutes(self):
        entries=campaign()
        self.assertEqual(len(entries),15)
        self.assertNotIn("PILOT", [s for s,_ in entries])
        self.assertEqual(sum(configuration(s,r)["duration_node_s"] for s,r in entries),9000)

    def test_frozen_pulses_and_clock(self):
        for scenario in ("EX-03","EX-04"):
            recipe=configuration(scenario,1)
            self.assertEqual(recipe["clock_basis"],"per_node_uptime")
            for node in NODES:
                pulses=[a.at_s for a in actions(scenario) if a.node_id==node and a.kind=="motion"]
                self.assertEqual(pulses,list(range(15,600,30)))

    def test_mixed_phases_are_explicit_and_repeat_identical(self):
        self.assertEqual(scene("EX-05","node_01",0)["environment"],"DAY")
        self.assertEqual(scene("EX-05","node_01",1)["environment"],"TWILIGHT")
        self.assertEqual(scene("EX-05","node_01",2)["distance"],50)
        self.assertEqual(len([a for a in actions("EX-05") if a.kind=="motion"]),40)
        self.assertEqual(configuration("EX-05",1)["actions"],configuration("EX-05",3)["actions"])

    def test_invalid_repeat_and_unknown_scenario(self):
        for scenario,repeat in [("EX-01",2),("EX-02",0),("EX-05",4)]:
            with self.assertRaises(ValueError):configuration(scenario,repeat)
        with self.assertRaises(ValueError):actions("EX-99")

    def test_preparations_do_not_change_physical_schedule(self):
        physical=[a for a in actions("PILOT") if not a.kind.startswith("prepare-")]
        self.assertEqual([a.at_s for a in physical if a.node_id=="node_01"],[15,40,45,60,75])
        for action in actions("EX-05"):
            if action.kind=="scene":
                self.assertIn(action.at_s,[300,600])

    def test_scheduling_estimate_is_bounded_and_not_a_measured_clock(self):
        clock={"uptime_ms":10000,"monotonic_ns":1_000_000_000}
        self.assertEqual(predicted_uptime(clock,.5,2_000_000_000),10500)
        self.assertEqual(predicted_uptime(clock,1,100_000_000_000),11000)
        self.assertEqual(predicted_uptime(clock,1,0),10000)


class ArithmeticChecks(unittest.TestCase):
    def test_csv_boundary_and_raw_payload_integrity(self):
        rows=[row(),row(1,2000,2)]
        expected,_=calculate(rows,2)
        exported=[]
        for index,source in enumerate(rows):
            value=json.loads(source['payload'])
            record={key:json.dumps(v) if isinstance(v,list) else str(v) for key,v in value.items()}
            record.update(quality=source['quality'],continuity=source['continuity'])
            for field in ['total_energy_wh','auto_energy_wh','baseline_wh']:
                record[field]=str(999 if index==0 else expected[field])
            exported.append(record)
        self.assertEqual(compare_csv(rows,exported,expected),[])
        changed=copy.deepcopy(exported);changed[1]['power_sim_w']='12'
        self.assertTrue(compare_csv(rows,changed,expected))
        self.assertTrue(compare_csv(rows,exported[1:],expected))
        changed=copy.deepcopy(exported);changed[1]['auto_energy_wh']='nan'
        self.assertTrue(compare_csv(rows,changed,expected))

    def test_two_clocks_and_known_75_percent_fixture(self):
        rows=[row(n,n*2000,n*6) for n in range(31)]
        value,details=calculate(rows,180)
        self.assertAlmostEqual(value["total_energy_wh"],.1)
        self.assertAlmostEqual(value["baseline_wh"],.4)
        self.assertAlmostEqual(value["saving_percent"],75)
        self.assertEqual(value["valid_uptime_s"],60)
        self.assertEqual(value["covered_wall_s"],180)
        self.assertEqual(details[0]["excluded_reasons"],["FIRST_SAMPLE"])

    def test_day_baseline_null(self):
        value,_=calculate([row(environment="DAY",power_sim_w=0),row(1,2000,2,environment="DAY",power_sim_w=0)],2)
        self.assertIsNone(value["saving_percent"])

    def test_manual_fault_low_load_unknown_keep_total_only(self):
        for changes in [dict(mode="MANUAL"),dict(faults=["OPEN_LOAD"]),dict(current_adc=100),dict(environment="UNKNOWN")]:
            value,_=calculate([row(**changes),row(1,2000,2,**changes)],2)
            self.assertGreater(value["total_energy_wh"],0)
            self.assertEqual(value["auto_energy_wh"],0)

    def test_no_bridge_boot_gap_session_duplicate_quality_or_receive_clock(self):
        cases=[]
        cases.append(row(1,2000,2,boot_id="abcdef01"))
        cases.append(row(1,7000,2))
        changed=row(1,2000,2);changed["continuity"]="session2";cases.append(changed)
        cases.append(row(0,2000,2))
        changed=row(1,2000,2);changed["quality"]="INVALID";cases.append(changed)
        cases.append(row(1,2000,0))
        for second in cases:
            value,_=calculate([row(),second],3)
            self.assertEqual(value["total_energy_wh"],0)

    def test_filter_node_boundary_never_carries_previous_segment(self):
        value,segments=calculate([row(10,20000,20),row(11,22000,22)],2)
        self.assertEqual(segments[0]["total_energy_wh"],0)
        self.assertAlmostEqual(value["total_energy_wh"],6*2/3600)

    def test_stats_comparison_detects_clock_mix_and_omitted_exclusions(self):
        value,_=calculate([row(),row(1,2000,6)],6)
        self.assertEqual(compare_stats(value,copy.deepcopy(value)),[])
        wrong=copy.deepcopy(value);wrong["valid_uptime_s"]=6
        self.assertTrue(compare_stats(value,wrong))
        wrong=copy.deepcopy(value);wrong["excluded_intervals"]={}
        self.assertTrue(compare_stats(value,wrong))


if __name__=="__main__":unittest.main()
