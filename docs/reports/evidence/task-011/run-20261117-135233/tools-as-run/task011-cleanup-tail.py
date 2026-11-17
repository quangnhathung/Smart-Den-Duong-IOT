from pathlib import Path
from datetime import datetime,timezone
import json,os,signal,socket,time,shutil
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);p=OUT/'cleanup.json';value=json.loads(p.read_text());shutil.copyfile(p,OUT/'cleanup-initial.json')
owned=json.loads((OUT/'owned-dashboard-browser.json').read_text());pid=owned['controller_pid'];proc=Path(f'/proc/{pid}/cmdline')
if proc.exists():
    args=proc.read_bytes().decode().split('\0');assert '/tmp/task011-dashboard.cjs' in args[1:],args[:2]
    os.kill(pid,signal.SIGKILL);value['signals'].append({'pid':pid,'reason':'Verified owned QA controller kept its HTTP listener after SIGTERM closed Chrome; stopped after grace period'})
for _ in range(50):
    active=[]
    for port in value['ports_checked']:
        with socket.socket() as s:
            s.settimeout(.2)
            if s.connect_ex(('127.0.0.1',port))==0:active.append(port)
    if not active:break
    time.sleep(.1)
value['still_listening_ports']=active;value['status']='PASS' if not active else 'INCOMPLETE';value['completed_at']=datetime.now(timezone.utc).isoformat();p.write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'status':value['status'],'remaining_ports':active}));assert not active
