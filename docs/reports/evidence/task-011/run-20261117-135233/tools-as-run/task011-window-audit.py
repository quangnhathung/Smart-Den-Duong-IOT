from pathlib import Path
from datetime import datetime,timezone
from urllib.request import urlopen
import json,statistics,sqlite3,time
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);QA=Path(S['qa']);folder=OUT/'stability-02';start=json.loads((folder/'start.json').read_text());start_ns=start['start_monotonic_ns'];end_ns=start_ns+1800*10**9;assert time.monotonic_ns()>=end_ns
samples=[json.loads(l) for l in (folder/'samples.jsonl').open()];assert all(not s.get('problems') and not s.get('error') for s in samples)
probe={'status':'INCOMPLETE','last_observed_elapsed_seconds':samples[-1]['elapsed_s'],'probe_samples':len(samples),'observed_exit_code':143,'reason':'HTTP/resource probe process received SIGTERM before 1800s; precise cause not established. Raw MQTT recorder and backend continued. Probe log is not claimed as full-window coverage.'}
(folder/'api-probe-status.json').write_text(json.dumps(probe,indent=2)+'\n')
all_events=[]
for p in (OUT/'mqtt-events.jsonl',OUT/'mqtt-events-fast.jsonl'):
    for line in p.open():all_events.append(json.loads(line))
events=[e for e in all_events if start_ns<=e['monotonic_ns']<=end_ns]
connections=[e for e in events if e['event'] in ('connected','disconnected')];assert not connections,connections
assert not [e for e in events if e.get('topic','').endswith('/command')]
assert not [e for e in events if e.get('topic','').endswith('/availability') and e['payload'].get('status')=='OFFLINE']
backend=start['backend'];proc=Path(f"/proc/{backend['pid']}/stat");assert proc.exists() and proc.read_text().split()[21]==backend['proc_start_ticks']
def get(path):
    with urlopen('http://127.0.0.1:8001'+path,timeout=8) as r:return json.loads(r.read())
health=get('/api/health');assert health=={'status':'OK','database':True,'broker':True,'queue':True,'dropped_events':0},health
final_nodes=get('/api/nodes');assert all(n['connection']=='ONLINE' and n['telemetry']['boot_id']==start['boots'][n['node_id']] for n in final_nodes)
nodes={};db=sqlite3.connect('file:'+str(QA/'qa.db')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
for node,boot in start['boots'].items():
    complete=[e for e in all_events if e.get('topic','').endswith('/'+node+'/telemetry') and e['payload']['boot_id']==boot]
    before=[e for e in complete if e['monotonic_ns']<start_ns];a=[e for e in complete if start_ns<=e['monotonic_ns']<=end_ns];after=[e for e in complete if e['monotonic_ns']>end_ns]
    assert before and a and after,node
    assert (start_ns-before[-1]['monotonic_ns'])/1e9<10 and (after[0]['monotonic_ns']-end_ns)/1e9<10,node
    seq=[int(e['payload']['seq']) for e in a];gaps=[(x,y) for x,y in zip(seq,seq[1:]) if y!=x+1];assert not gaps,(node,gaps[:5]);assert seq[0]==int(before[-1]['payload']['seq'])+1 and int(after[0]['payload']['seq'])==seq[-1]+1
    assert all(e['payload']['node_id']==node and e['payload']['mode']=='AUTO' and not e['payload']['faults'] for e in a)
    up=[int(e['payload']['uptime_ms']) for e in a];assert all(y>x for x,y in zip(up,up[1:])),node
    wall=[(y['monotonic_ns']-x['monotonic_ns'])/1e6 for x,y in zip(a,a[1:])];assert max(wall)<10000,(node,max(wall))
    stored={int(r['seq']):dict(r) for r in db.execute('SELECT * FROM telemetry WHERE node_id=? AND boot_id=?',(node,boot))};continuity=set();max_skew=0
    for e in a:
        t=e['payload'];row=stored[int(t['seq'])];assert row['quality']=='ACCEPTED' and json.loads(row['payload'])==t,(node,t['seq']);continuity.add(row['continuity']);max_skew=max(max_skew,abs(row['received_at']*1000-e['host_ms']))
    assert len(continuity)==1,(node,continuity)
    nodes[node]={'boot_id':boot,'received_messages':len(a),'first_seq':seq[0],'last_seq':seq[-1],'missing_sequences':gaps,'all_raw_messages_match_accepted_sqlite_rows':True,'continuity_keys':sorted(continuity),'max_recorder_backend_receipt_skew_ms':max_skew,'median_arrival_gap_wall_ms':statistics.median(wall),'max_arrival_gap_wall_ms':max(wall),'node_elapsed_simulated_s':(up[-1]-up[0])/1000,'received_span_wall_s':(a[-1]['monotonic_ns']-a[0]['monotonic_ns'])/1e9,'boundary_before_monotonic_ns':before[-1]['monotonic_ns'],'boundary_after_monotonic_ns':after[0]['monotonic_ns']}
check=db.execute('PRAGMA quick_check').fetchone()[0];assert check=='ok';db.close()
wire={'status':'PASS','window':'stability-02','start_monotonic_ns':start_ns,'end_monotonic_ns':end_ns,'duration_real_seconds':1800.0,'audit_elapsed_since_start_seconds':(time.monotonic_ns()-start_ns)/1e9,'raw_recorder_reconnects_in_window':connections,'commands_in_window':0,'nodes':nodes,'backend_pid_and_start_ticks_unchanged':True,'final_health':health,'database_quick_check':check,'api_probe':probe,'clock_basis':'Fixed original 1800 host monotonic seconds, not sum of node uptime. Continuous raw telemetry and identical accepted SQLite rows bracket and cover the full interval. Periodic arrival gap differs from causal sensor→DOM latency.'}
(folder/'wire-audit.json').write_text(json.dumps(wire,indent=2)+'\n')
summary={'status':'PASS','basis':'Independent continuous raw MQTT + accepted SQLite + unchanged backend process + final zero-drop health; HTTP probes partial and explicitly INCOMPLETE','elapsed_seconds':1800.0,'ended_at':datetime.fromtimestamp(start['start_wall_ms']/1000+1800,timezone.utc).isoformat(),'audited_at':datetime.now(timezone.utc).isoformat(),'samples':len(samples),'initial':start,'final_nodes':final_nodes,'final_health':health,'errors':[],'database_quick_check':check,'wire_audit':'wire-audit.json','api_probe':'api-probe-status.json'}
(folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'status':'PASS','duration_real_seconds':1800,'messages_by_node':{n:v['received_messages'] for n,v in nodes.items()},'api_probe_status':probe['status'],'backend_unchanged':True}))
