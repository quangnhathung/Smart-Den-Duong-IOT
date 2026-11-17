from pathlib import Path
import json,os,signal,subprocess,time,shutil,socket
S=json.loads(Path('/tmp/task011-active.json').read_text());QA=Path(S['qa']);OUT=Path(S['evidence']);owned=json.loads((QA/'owned-processes.json').read_text());old=next(p for p in owned if p['name']=='observer');p=Path(f"/proc/{old['pid']}/stat");assert p.read_text().split()[21]==old['proc_start_ticks'];os.kill(old['pid'],signal.SIGTERM)
for i in range(50):
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',18771))!=0:break
    time.sleep(.1)
script=Path('/tmp/task011-observe.py');(OUT/'tools-as-run').mkdir(exist_ok=True);shutil.copyfile(script,OUT/'tools-as-run/observer-initial.py')
s=script.read_text().replace("OUT/'mqtt-events.jsonl'", "OUT/'mqtt-events-fast.jsonl'").replace("client_id='task011-observer'", "client_id='task011-observer-fast'").replace("client.on_connect=connected;", "client.reconnect_delay_set(min_delay=1,max_delay=2);client.on_connect=connected;").replace("{'latest':LATEST,'events_count':len(EVENTS)}", "{'latest':LATEST,'events_count':len(EVENTS),'connected':client.is_connected()}");script.write_text(s)
p=subprocess.Popen([str(Path(S['root']).parent/'backend/.venv/bin/python'),'-B',str(script)],stdout=(OUT/'observer-fast.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
owned.append({'name':'observer-fast','pid':p.pid,'args':[str(script)],'proc_start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21]});(QA/'owned-processes.json').write_text(json.dumps(owned,indent=2)+'\n')
for name in ('broker-outage-start.json','auto-offline-serial.json'):
    path=OUT/name
    if path.exists():shutil.copyfile(path,OUT/('initial-'+name))
print('Started fast-reconnecting QA recorder; original stream and first outage evidence preserved')
