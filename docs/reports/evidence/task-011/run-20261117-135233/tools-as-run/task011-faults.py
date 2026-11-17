import sys,time,json,subprocess,runpy,signal,os,sqlite3,hashlib
from datetime import datetime,timezone
from pathlib import Path
H=runpy.run_path('/tmp/task011-livechecks.py');request,wait,save,NODES=(H[k] for k in ('request','wait','save','NODES'))
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);QA=Path(S['qa'])
def ui(path,body):return request(path,body,18772,40)
def ldr(index):
    subprocess.run(['python3','/tmp/task011-arrange.py',str(index)],check=True,stdout=subprocess.DEVNULL)
    s=ui('/inspect',{'node':index})
    if 'ILLUMINATION' not in s['text']:ui('/part',{'node':index,'part':'wokwi-photoresistor-sensor#ldr'})
def key(index,key):return ui('/key',{'node':index,'key':key})
def record_case(name,value):save(name,{'status':'PASS',**value});print(name,'PASS',flush=True)
def db_counts():
    with sqlite3.connect('file:'+str(QA/'qa.db')+'?mode=ro',uri=True) as db:
        return {table:db.execute('SELECT count(*) FROM '+table).fetchone()[0] for table in ('telemetry','commands','alerts','boots')}
def fingerprint(cutoff=None):
    with sqlite3.connect('file:'+str(QA/'qa.db')+'?mode=ro',uri=True) as db:
        if cutoff is None:cutoff=db.execute('SELECT max(rowid) FROM telemetry').fetchone()[0]
        rows=db.execute('SELECT * FROM telemetry WHERE rowid<=? ORDER BY rowid',(cutoff,)).fetchall()
        return {'cutoff':cutoff,'rows':len(rows),'sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()}
phase=sys.argv[1]
if phase=='steady-auto':
    before=request('/api/nodes')
    for i in (1,2,3):ldr(i);key(i,'Home')
    after=wait(lambda ns:all(n['telemetry']['mode']=='AUTO' and n['telemetry']['environment']=='NIGHT' and n['telemetry']['brightness_applied']==25 and not n['faults'] for n in ns),30)
    record_case('postflight-steady-auto.json',{'before':before,'after':after,'note':'Normal sensor workload inside stability window; no commands or restart'})
elif phase=='stop-serial':
    before=request('/api/nodes');pids=[]
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:args=(p/'cmdline').read_bytes().decode().split('\0')
        except (OSError,UnicodeError):continue
        if '/tmp/task011-serial-observer.py' in args[1:]:pids.append(int(p.name))
    assert len(pids)==1,pids
    for pid in pids:os.kill(pid,signal.SIGTERM)
    time.sleep(2);after=request('/api/nodes');assert all(a['telemetry']['boot_id']==b['telemetry']['boot_id'] for a,b in zip(after,before))
    record_case('serial-observer-stop.json',{'pids':pids,'before':before,'after':after,'host_ms':time.time()*1000})
elif phase=='restart-all':
    before=request('/api/nodes')
    for i in (1,2,3):
        ui('/palette',{'node':i});ui('/type',{'node':i,'text':'Stop Simulation'});ui('/enter',{'node':i})
    for i in (1,2,3):
        ui('/palette',{'node':i});ui('/type',{'node':i,'text':'Wokwi: Start Simulator'});ui('/enter',{'node':i})
    nodes=wait(lambda ns:all(n['connection']=='ONLINE' and n['freshness']=='FRESH' and n['telemetry']['boot_id']!=before[j]['telemetry']['boot_id'] for j,n in enumerate(ns)),60)
    record_case('runtime-cpu4-preflight.json',{'before':before,'nodes':nodes})
elif phase=='start':
    for i in (1,2,3):
        ui('/palette',{'node':i});v=ui('/type',{'node':i,'text':'Wokwi: Start Simulator'});assert 'Wokwi: Start Simulator' in v['text'];ui('/enter',{'node':i})
    nodes=wait(lambda ns:all(n['connection']=='ONLINE' and n['freshness']=='FRESH' for n in ns),60)
    record_case('runtime-final-preflight.json',{'nodes':nodes})
elif phase=='sensors':
    for i in (1,2,3):ldr(i);key(i,'End')
    baseline=wait(lambda ns:all(n['telemetry']['ldr_adc']<100 and n['telemetry']['environment']=='DAY' and n['telemetry']['brightness_applied']==0 for n in ns));cases=[]
    for i,node in enumerate(NODES,1):
        before=request('/api/nodes');key(i,'Home');after=wait(lambda ns:ns[i-1]['telemetry']['environment']=='NIGHT' and ns[i-1]['telemetry']['brightness_applied']==25)
        for j in range(3):
            if j!=i-1:
                for field in ('ldr_adc','mode','brightness_target','brightness_applied','faults'):assert before[j]['telemetry'][field]==after[j]['telemetry'][field],(node,field)
        cases.append({'node_id':node,'before':before,'after':after});key(i,'End');wait(lambda ns:ns[i-1]['telemetry']['ldr_adc']<100 and ns[i-1]['telemetry']['environment']=='DAY' and ns[i-1]['telemetry']['brightness_applied']==0)
    record_case('sensor-isolation.json',{'cases':cases})
elif phase=='load':
    ldr(2);key(2,'Home');before=wait(lambda ns:ns[1]['telemetry']['brightness_applied']==25 and ns[1]['telemetry']['environment']=='NIGHT')
    info=ui('/part',{'node':2,'part':'wokwi-potentiometer#currentSim'});save('load-control-inspection.json',info);print('Potentiometer sliders',len(info['sliders']),flush=True)
    ui('/key',{'node':2,'index':1,'key':'Home'});fault=wait(lambda ns:'OPEN_LOAD' in ns[1]['faults'],25)
    assert all(not n['faults'] for n in (fault[0],fault[2]))
    ui('/key',{'node':2,'index':1,'key':'End'});recovered=wait(lambda ns:not ns[1]['faults'] and ns[1]['telemetry']['current_adc']==4095,25)
    record_case('open-load-isolation.json',{'before':before,'fault':fault,'recovered':recovered,'alerts':request('/api/alerts')})
elif phase=='node-stop':
    before=request('/api/nodes');ui('/palette',{'node':2});s=ui('/type',{'node':2,'text':'Stop Simulation'});assert 'Stop Simulation' in s['text'];ui('/enter',{'node':2})
    down=wait(lambda ns:ns[1]['connection']=='OFFLINE' and ns[0]['freshness']=='FRESH' and ns[2]['freshness']=='FRESH',30)
    controls=[]
    for node in ('node_01','node_03'):
        r=H['command'](node,{'mode':'MANUAL','brightness':80});controls.append(r);H['command'](node,{'mode':'AUTO'})
    ui('/palette',{'node':2});s=ui('/type',{'node':2,'text':'Wokwi: Start Simulator'});assert 'Wokwi: Start Simulator' in s['text'];ui('/enter',{'node':2});up=wait(lambda ns:all(n['connection']=='ONLINE' and n['freshness']=='FRESH' for n in ns),45)
    assert up[1]['telemetry']['boot_id']!=before[1]['telemetry']['boot_id'];assert all(up[j]['telemetry']['boot_id']==before[j]['telemetry']['boot_id'] for j in (0,2))
    record_case('node-stop-isolation.json',{'before':before,'down':down,'controls_on_other_nodes':controls,'up':up})
elif phase=='broker-down':
    assert request('/state',port=18771)['connected']
    for i in (1,2,3):ldr(i);key(i,'End')
    wait(lambda ns:all(n['telemetry']['ldr_adc']<100 and n['telemetry']['brightness_applied']==0 for n in ns),30)
    conf=QA/'mosquitto.conf'
    if 'log_type all' not in conf.read_text():conf.write_text(conf.read_text()+'log_type all\n')
    before=request('/api/nodes');event_index=request('/state',port=18771)['events_count'];broker=json.loads((OUT/'owned-broker.json').read_text());label=subprocess.check_output(['docker','inspect','--format','{{index .Config.Labels "smartlight.qa"}}',broker['name']],text=True).strip();assert label==broker['label']
    commands=[request(f'/api/nodes/{n}/commands',{'mode':'MANUAL','brightness':80}) for n in NODES]
    subprocess.run(['docker','stop','-t','1',broker['name']],check=True,capture_output=True)
    down=wait(lambda ns:all(n['connection']=='OFFLINE' for n in ns),30)
    save('broker-outage-start.json',{'before':before,'down':down,'commands':commands,'event_index':event_index,'down_monotonic_ns':time.monotonic_ns(),'down_host_ms':time.time()*1000})
    for i in (1,2,3):ldr(i);key(i,'Home')
    print('Broker down, sensors set NIGHT; read-only Serial must corroborate AUTO/PWM25 on all three',flush=True)
elif phase=='broker-up':
    start=json.loads((OUT/'broker-outage-start.json').read_text());broker=json.loads((OUT/'owned-broker.json').read_text());up_started=datetime.now(timezone.utc).isoformat();subprocess.run(['docker','start',broker['name']],check=True,capture_output=True)
    up=wait(lambda ns:all(n['freshness']=='FRESH' and n['connection']=='ONLINE' and n['telemetry']['mode']=='AUTO' and n['telemetry']['brightness_applied']==25 for n in ns),45)
    assert all(a['telemetry']['boot_id']==b['telemetry']['boot_id'] for a,b in zip(up,start['before']))
    events=request('/events?from='+str(start['event_index']),port=18771)
    for c in start['commands']:
        pubs=[e for e in events if e.get('topic','').endswith('/command') and e.get('payload',{}).get('command_id')==c['command_id']]
        assert not any(e['host_ms']>start['down_host_ms']+1000 for e in pubs),pubs
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        recorder=request('/state',port=18771)
        if recorder['connected'] and all(n in recorder['latest'] and recorder['latest'][n]['host_ms']>datetime.fromisoformat(up_started).timestamp()*1000 for n in NODES):break
        time.sleep(.2)
    else:raise RuntimeError('MQTT recorder not synchronized after reconnect')
    broker_log=subprocess.run(['docker','logs','--since',up_started,broker['name']],capture_output=True,text=True,check=True)
    before_new=broker_log.stdout+broker_log.stderr;save('broker-reconnect-no-replay-checkpoint.json',{'up_started':up_started,'recorder':recorder,'broker_log':before_new})
    assert not any('/command' in line and 'PUBLISH' in line for line in before_new.splitlines()),before_new
    new=[H['command'](node,{'mode':'AUTO'}) for node in NODES]
    record_case('broker-outage-recovery.json',{'start':start,'up':up,'events':events,'fresh_commands':new})
elif phase=='backend-restart':
    before=request('/api/nodes');counts=db_counts();old_data=fingerprint();owned=json.loads((QA/'owned-processes.json').read_text());old=next(p for p in reversed(owned) if p['name']=='backend');assert Path(f"/proc/{old['pid']}/stat").read_text().split()[21]==old['proc_start_ticks']
    os.kill(old['pid'],signal.SIGTERM)
    for i in range(40):
        if not Path(f"/proc/{old['pid']}").exists():break
        time.sleep(.1)
    env=dict(os.environ);env.update(SMARTLIGHT_DB=str(QA/'qa.db'),SMARTLIGHT_MQTT_HOST='127.0.0.1',SMARTLIGHT_MQTT_PORT='1883',PYTHONDONTWRITEBYTECODE='1')
    p=subprocess.Popen(old['args'],cwd=Path(S['root']).parent/'backend',env=env,stdout=(OUT/'backend-restarted.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
    owned.append({'name':'backend','pid':p.pid,'args':old['args'],'proc_start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21]});(QA/'owned-processes.json').write_text(json.dumps(owned,indent=2)+'\n')
    time.sleep(1);up=wait(lambda ns:all(n['connection']=='ONLINE' and n['freshness']=='FRESH' for n in ns),25);after_counts=db_counts();preserved=fingerprint(old_data['cutoff']);assert preserved==old_data,(old_data,preserved)
    assert all(after_counts[k]>=counts[k] for k in counts);assert all(a['telemetry']['boot_id']==b['telemetry']['boot_id'] for a,b in zip(up,before))
    record_case('backend-restart.json',{'before':before,'after':up,'counts_before':counts,'counts_after':after_counts,'old_telemetry_before':old_data,'old_telemetry_after':preserved,'pid_before':old['pid'],'pid_after':p.pid})
else:raise SystemExit('Unknown phase')
