"""Read captured evidence and independently check clocks, energy and preserved rows."""
import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--after', help='sqlite snapshot tag taken after actual restart')
parser.add_argument('--tag', required=True)
args = parser.parse_args()


def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))


initial = read('sqlite-initial.json')
samples = initial['tables']['telemetry']
transitions = []
previous = None
gaps = []
for row in samples:
    value = json.loads(row['payload'])
    if previous is None or value['mode'] != previous[1]['mode']:
        transitions.append(dict(seq=value['seq'], uptime_ms=value['uptime_ms'], mode=value['mode'],
                                target=value['brightness_target'], applied=value['brightness_applied'],
                                received_at_unix=row['received_at']))
    if previous and row['boot_id'] == previous[0]['boot_id']:
        dt_node=(value['uptime_ms']-previous[1]['uptime_ms'])/1000
        dt_wall=row['received_at']-previous[0]['received_at']
        gaps.append(dict(node_seconds=dt_node, wall_seconds=dt_wall))
    previous=(row,value)

result=dict(historical_manual=dict(commands=initial['tables']['commands'],
                                  ack_events=initial['tables']['ack_events'],transitions=transitions,
                                  samples_with_applied80=sum(json.loads(r['payload'])['brightness_applied']==80
                                                            for r in samples)),
            historical_timing=dict(pair_count=len(gaps),wall_gap_max_s=max(x['wall_seconds'] for x in gaps),
                gaps_ge10_wall_s=sum(x['wall_seconds']>=10 for x in gaps),
                node_to_wall_median_ratio=statistics.median(x['node_seconds']/x['wall_seconds'] for x in gaps
                                                          if x['wall_seconds']>0),
                note='Sampling can be slower in wall time. Sensor action-to-render latency not measured by this ratio.'),
            energy=[],persistence=dict(result='PENDING',reason='No post-restart snapshot provided'))

for path in sorted(ROOT.glob('experiment-*.csv')):
    with path.open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream))
    previous={}
    checked=0
    boundary_count=0
    total=0
    for row in rows:
        node=row['node_id']
        prior=previous.get(node)
        duration=float(row['valid_uptime_s'])
        calculated=0
        if prior:
            delta=(int(row['uptime_ms'])-int(prior['uptime_ms']))/1000
            eligible=(row['quality']==prior['quality']=='ACCEPTED' and
                      row['boot_id']==prior['boot_id'] and row['continuity']==prior['continuity'] and
                      int(row['seq'])>int(prior['seq']) and 0<delta<=6 and row['received_at']>prior['received_at'])
            if eligible:
                calculated=(float(prior['power_sim_w'])+float(row['power_sim_w']))/2*delta/3600
                assert math.isclose(duration,delta,abs_tol=1e-10)
            else:
                assert duration==0
            if row['continuity']!=prior['continuity']:
                boundary_count+=1
                assert duration==0 and float(row['total_energy_wh'])==0
        else:
            assert duration==0
        assert math.isclose(calculated,float(row['total_energy_wh']),rel_tol=1e-9,abs_tol=1e-10)
        model_power=12*(2000*int(row['brightness_applied'])/100*int(row['current_adc'])/4095)/1000
        # Firmware serializes finite decimals: allow a micro-watt rounding margin.
        assert math.isclose(float(row['power_sim_w']),model_power,abs_tol=1e-5)
        total+=calculated
        checked+=1
        previous[node]=row
    result['energy'].append(dict(file=path.name,result='PASS',rows=checked,independent_energy_wh=total,
                                 continuity_boundaries=boundary_count,nonzero_power_rows=sum(float(x['power_sim_w'])>0 for x in rows)))

if args.after:
    before=read('sqlite-before-restart.json')['tables']
    after=read('sqlite-'+args.after+'.json')['tables']
    preservation={}
    for table in ['telemetry','commands','ack_events','alerts','experiments','availability']:
        key='command_id' if table=='commands' else 'id'
        later={str(row[key]):row for row in after[table]}
        missing=[row[key] for row in before[table] if str(row[key]) not in later]
        assert not missing,(table,missing)
        # Immutable telemetry/ACK/availability must retain exact content. Alerts and commands can evolve.
        if table in ['telemetry','ack_events','availability']:
            assert all(row==later[str(row[key])] for row in before[table]),table
        preservation[table]=dict(before=len(before[table]),after=len(after[table]),missing=missing)
    result['persistence']=dict(result='PASS',rows=preservation,
                              limitation='Must corroborate with actual API outage/restart and continuity evidence')

with (ROOT/f'audit-{args.tag}.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps(dict(energy=result['energy'],persistence=result['persistence'],timing=result['historical_timing']),indent=2))
