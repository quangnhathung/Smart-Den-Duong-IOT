"""Read-only verification of two new telemetry samples through Backend proxy1884."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT=Path(__file__).resolve().parent
initial=json.loads((ROOT/'sqlite-baseline.json').read_text(encoding='utf-8'))
baseline=initial['tables']['telemetry'][-1]
samples=[];seen=set()
with (ROOT/'proxy-preflight.jsonl').open('x',encoding='utf-8',buffering=1) as output:
    with httpx.Client(base_url='http://127.0.0.1:8001',trust_env=False,timeout=3) as client:
        deadline=time.monotonic()+60
        while time.monotonic()<deadline and len(samples)<2:
            status=json.loads((ROOT/'ack-delay-status.json').read_text(encoding='utf-8'))
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(status['at'])).total_seconds()
            assert status['listening'] and len(status['backend_clients'])==1 and age<3
            assert not status['targets'],'Proxy must not be armed before preflight'
            health=client.get('/api/health');nodes=client.get('/api/nodes')
            output.write(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'proxy':status,
                                     'health_status':health.status_code,'health':health.json(),
                                     'nodes_status':nodes.status_code,'nodes':nodes.json()})+'\n')
            assert health.status_code==200 and health.json()['status']=='OK' and health.json()['dropped_events']==0
            assert nodes.status_code==200
            node=next(x for x in nodes.json() if x['node_id']=='node_01')
            value=node['telemetry']
            if (node['freshness']=='FRESH' and node['age_s']<=3 and value and
                int(value['seq'])>int(baseline['seq']) and value['seq'] not in seen):
                assert value['boot_id']==baseline['boot_id']
                assert value['mode']=='AUTO' and value['brightness_target']==value['brightness_applied']==25
                seen.add(value['seq']);samples.append(node)
            time.sleep(.4)
        assert len(samples)==2,'Two new telemetry samples were not verified; do not send command'
result={'result':'PASS','scope':'Before test: Backend1884 forwarding two fresh real node_01 telemetry samples',
        'baseline_seq':baseline['seq'],'samples':samples,'proxy':status,'commands_sent':0}
with (ROOT/'proxy-preflight.json').open('x',encoding='utf-8') as output:json.dump(result,output,indent=2)
print('PROXY_TELEMETRY_PREFLIGHT PASS', [x['telemetry']['seq'] for x in samples],flush=True)
