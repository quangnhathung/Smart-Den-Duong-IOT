import json,time,sys,sqlite3,os
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime,timezone
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);QA=Path(S['qa']);DURATION=1800;folder=OUT/(sys.argv[1] if len(sys.argv)>1 else 'stability-01');folder.mkdir(exist_ok=False)
def get(path,port=8001):
    with urlopen(f'http://127.0.0.1:{port}'+path,timeout=3) as r:return json.loads(r.read())
def utc():return datetime.now(timezone.utc).isoformat()
def resources():
    mem={}
    for line in Path('/proc/meminfo').read_text().splitlines():
        name,v=line.split(':',1)
        if name in ('MemTotal','MemAvailable','SwapTotal','SwapFree'):mem[name]=int(v.strip().split()[0])
    return {'mem_kib':mem,'loadavg':os.getloadavg()}
initial=get('/api/nodes');health=get('/api/health');assert len(initial)==3 and all(n['freshness']=='FRESH' and n['connection']=='ONLINE' and n['telemetry']['mode']=='AUTO' and not n['faults'] for n in initial),initial
assert health=={'status':'OK','database':True,'broker':True,'queue':True,'dropped_events':0},health
owned=json.loads((QA/'owned-processes.json').read_text());backend=next(p for p in reversed(owned) if p['name']=='backend');boots={n['node_id']:n['telemetry']['boot_id'] for n in initial};last={n['node_id']:(int(n['telemetry']['seq']),int(n['telemetry']['uptime_ms'])) for n in initial}
start=time.monotonic_ns();wall=time.time();errors=[];warnings=[];max_age={n:0 for n in boots};count=0;last_print=0;changed={n:0 for n in boots}
meta={'started_at':utc(),'start_monotonic_ns':start,'start_wall_ms':wall*1000,'required_seconds':DURATION,'boots':boots,'backend':backend,'initial_nodes':initial,'initial_health':health,'runtime':'Sensor-change coalescing fixed; independent profiles; CPU cap4; product timers unchanged','artifact_manifests':{f'node_0{i}':json.loads((OUT/f'node_0{i}-artifact-manifest-final.json').read_text()) for i in (1,2,3)}}
(folder/'start.json').write_text(json.dumps(meta,indent=2)+'\n');print('STABILITY_STARTED',meta['started_at'],flush=True)
log=(folder/'samples.jsonl').open('w',buffering=1)
while True:
    elapsed=(time.monotonic_ns()-start)/1e9
    try:
        nodes=get('/api/nodes');h=get('/api/health');problems=[]
        if h['status']!='OK' or not all(h[k] for k in ('database','broker','queue')) or h['dropped_events']!=0:problems.append({'health':h})
        proc=Path(f"/proc/{backend['pid']}/stat")
        if not proc.exists() or proc.read_text().split()[21]!=backend['proc_start_ticks']:problems.append('Backend process changed or stopped')
        if set(n['node_id'] for n in nodes)!=set(boots):problems.append('Node set changed')
        for n in nodes:
            node=n['node_id'];t=n['telemetry'];seq,up=int(t['seq']),int(t['uptime_ms']);previous=last[node]
            if t['boot_id']!=boots[node]:problems.append({'node':node,'unexpected_boot':t['boot_id']})
            if seq<previous[0] or up<previous[1]:problems.append({'node':node,'sequence_or_uptime_regressed':(seq,up),'previous':previous})
            if seq>previous[0]:changed[node]+=1
            last[node]=(seq,up);max_age[node]=max(max_age[node],n['age_s'])
            if n['connection']!='ONLINE' or n['age_s']>10:problems.append({'node':node,'connection':n['connection'],'age_s':n['age_s']})
            if t['mode']!='AUTO' or n['faults']:problems.append({'node':node,'mode':t['mode'],'faults':n['faults']})
            if n['freshness']!='FRESH':warnings.append({'elapsed_s':elapsed,'node':node,'freshness':n['freshness'],'age_s':n['age_s']})
        if problems:errors.append({'elapsed_s':elapsed,'problems':problems})
        value={'elapsed_s':elapsed,'monotonic_ns':time.monotonic_ns(),'wall_ms':time.time()*1000,'nodes':nodes,'health':h,'problems':problems}
        if count%15==0:value['resources']=resources()
        log.write(json.dumps(value)+'\n');count+=1
    except Exception as e:
        errors.append({'elapsed_s':elapsed,'error':str(e)});log.write(json.dumps({'elapsed_s':elapsed,'error':str(e)})+'\n')
    elapsed=(time.monotonic_ns()-start)/1e9
    if elapsed-last_print>=60 or elapsed>=DURATION:
        progress={'elapsed_s':elapsed,'remaining_s':max(0,DURATION-elapsed),'samples':count,'errors':len(errors),'stale_observations':len(warnings),'changed_samples':changed,'max_age_s':max_age}
        (folder/'progress.json').write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True);last_print=elapsed
    if elapsed>=DURATION:break
    time.sleep(min(2,DURATION-elapsed))
log.close()
with sqlite3.connect('file:'+str(QA/'qa.db')+'?mode=ro',uri=True) as db:
    quick=db.execute('PRAGMA quick_check').fetchone()[0]
    counts=dict(db.execute('SELECT node_id,count(*) FROM telemetry GROUP BY node_id').fetchall())
if quick!='ok':errors.append({'database_quick_check':quick})
if not all(changed.values()):errors.append({'missing_node_progress':changed})
summary={'status':'PASS' if not errors else 'FAIL','ended_at':utc(),'elapsed_seconds':(time.monotonic_ns()-start)/1e9,'required_seconds':DURATION,'samples':count,'initial':meta,'final_nodes':get('/api/nodes'),'final_health':get('/api/health'),'errors':errors,'stale_observations':warnings,'changed_samples':changed,'max_age_s':max_age,'database_quick_check':quick,'telemetry_counts':counts}
(folder/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('STABILITY_'+summary['status'],summary['elapsed_seconds'],flush=True)
