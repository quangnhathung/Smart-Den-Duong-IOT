import json,time,sys
from pathlib import Path
from urllib.request import Request,urlopen
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);NODES=['node_01','node_02','node_03']
def request(path,body=None,port=8001,timeout=12):
    data=None if body is None else json.dumps(body).encode()
    with urlopen(Request(f'http://127.0.0.1:{port}'+path,data=data,headers={'Content-Type':'application/json'}),timeout=timeout) as r:return json.loads(r.read())
def wait(predicate,timeout=18):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        v=request('/api/nodes')
        if predicate(v):return v
        time.sleep(.2)
    raise RuntimeError('Node predicate timed out: '+str(v))
def save(name,v):(OUT/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def command(node,body):
    before=wait(lambda ns:next(n for n in ns if n['node_id']==node)['can_command'] and next(n for n in ns if n['node_id']==node)['age_s']<1.0);start=time.time()*1000;index=request('/state',port=18771)['events_count'];row=request(f'/api/nodes/{node}/commands',body);identifier=row['command_id'];end=time.monotonic()+13
    while time.monotonic()<end:
        row=request('/api/commands/'+identifier)
        if row['result']!='PENDING':break
        time.sleep(.05)
    assert row['result']=='APPLIED',row
    expected=body['brightness'] if body['mode']=='MANUAL' else {'DAY':0,'TWILIGHT':50,'NIGHT':25,'UNKNOWN':50}[next(n for n in before if n['node_id']==node)['telemetry']['environment']]
    after=wait(lambda ns:next(n for n in ns if n['node_id']==node)['telemetry']['brightness_applied']==expected and next(n for n in ns if n['node_id']==node)['telemetry']['mode']==body['mode'])
    for b,a in zip(before,after):
        if b['node_id']!=node:
            for field in ('mode','brightness_target','brightness_applied','ldr_adc','faults'):assert a['telemetry'][field]==b['telemetry'][field],(node,field,b,a)
    events=request('/events?from='+str(index),port=18771)
    sent=[e for e in events if e.get('topic','').endswith('/command') and e.get('payload',{}).get('command_id')==identifier]
    ack=[e for e in events if e.get('topic','').endswith('/ack') and e.get('payload',{}).get('command_id')==identifier]
    for _ in range(10):
        if ack:break
        time.sleep(.1);events=request('/events?from='+str(index),port=18771)
        ack=[e for e in events if e.get('topic','').endswith('/ack') and e.get('payload',{}).get('command_id')==identifier]
    assert ack and all(e['payload']['node_id']==node for e in ack)
    return {'node_id':node,'request':body,'request_host_ms':start,'status':'PASS','command':row,'before':before,'after':after,'mqtt_commands':sent,'mqtt_ack':ack,'mqtt_command_ack_ms':ack[0]['host_ms']-sent[0]['host_ms'] if sent else None}
if __name__=='__main__':
    phase=sys.argv[1]
    if phase=='commands':
        rows=[]
        for node in NODES:
            for body in [{'mode':'MANUAL','brightness':20},{'mode':'AUTO'},{'mode':'MANUAL','brightness':40},{'mode':'AUTO'},{'mode':'MANUAL','brightness':60},{'mode':'AUTO'},{'mode':'MANUAL','brightness':80},{'mode':'AUTO'},{'mode':'MANUAL','brightness':80},{'mode':'AUTO'}]:
                row=command(node,body);rows.append(row);save('command-isolation-latency.json',rows);print(node,len([r for r in rows if r['node_id']==node]),'PASS',row['mqtt_command_ack_ms'],flush=True)
    elif phase=='manual-timeout':
        starts=[]
        for node in NODES:
            wait(lambda ns:next(n for n in ns if n['node_id']==node)['can_command'] and next(n for n in ns if n['node_id']==node)['age_s']<1.0)
            row=request(f'/api/nodes/{node}/commands',{'mode':'MANUAL','brightness':80});starts.append(row)
        before=wait(lambda ns:all(n['telemetry']['mode']=='MANUAL' and n['telemetry']['brightness_applied']==80 for n in ns));print('All three MANUAL80; waiting real firmware timeout',flush=True)
        after=wait(lambda ns:all(n['telemetry']['mode']=='AUTO' and n['telemetry']['brightness_applied']==n['telemetry']['brightness_target'] for n in ns),timeout=240)
        save('manual-timeout.json',{'status':'PASS','commands':starts,'manual':before,'auto':after,'elapsed_uptime_ms':{n['node_id']:int(n['telemetry']['uptime_ms'])-int(b['telemetry']['uptime_ms']) for n,b in zip(after,before)}});print('Three node MANUAL timeout PASS',flush=True)
