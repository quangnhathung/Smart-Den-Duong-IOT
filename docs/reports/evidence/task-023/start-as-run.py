import datetime,json,os,socket,subprocess,time
from pathlib import Path
root=Path('/home/quangnhathung/HungQuang_WorkSpace/Learing/Iot/DoAn/firmware')
out=root/'output/task-023';out.mkdir(exist_ok=True)
meta={'at':datetime.datetime.now().astimezone().isoformat(),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'processes':[]}
def save(): (out/'startup.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
def run(args,cwd=root):
 r=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=50)
 print(json.dumps({'args':args,'exit':r.returncode,'stdout':r.stdout[-1800:],'stderr':r.stderr[-1000:]},ensure_ascii=False),flush=True)
 if r.returncode:raise RuntimeError(args)
 return r
extensions=run(['code','--list-extensions']).stdout.splitlines()
assert 'wokwi.wokwi-vscode' in extensions
assert any(x.lower()=='ritwickdey.liveserver' for x in extensions)
run([str(root.parent/'backend/.venv/bin/python'),'-c','import uvicorn,fastapi,paho.mqtt.client; print("backend runtime ready")'])
for port in [1883,8000,5500,4000,4001,4002]:
 with socket.socket() as s:assert s.connect_ex(('127.0.0.1',port))!=0,('port already occupied',port)
run(['docker','compose','-f','infra/compose.yaml','up','-d','--pull','never','mosquitto'])
meta['broker']=json.loads(run(['docker','inspect','smartlight-p0-mosquitto-1']).stdout)[0] if False else run(['docker','compose','-f','infra/compose.yaml','ps','--format','json']).stdout
save()
backend=root.parent/'backend';db=backend/'data/smartlight.db'
assert db.is_file(), 'Existing DB expected'
meta['database']=str(db)
env=os.environ.copy();env.update(SMARTLIGHT_DB=str(db),SMARTLIGHT_MQTT_HOST='127.0.0.1',SMARTLIGHT_MQTT_PORT='1883')
args=[str(backend/'.venv/bin/python'),'-m','uvicorn','smartlight.api:app','--host','127.0.0.1','--port','8000','--workers','1']
with (out/'backend.log').open('ab',buffering=0) as log:
 p=subprocess.Popen(args,cwd=backend,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
time.sleep(1)
assert p.poll() is None,(out/'backend.log').read_text()[-3000:]
meta['processes'].append({'role':'backend','pid':p.pid,'start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21],'args':args,'log':str(out/'backend.log')});save()
for folder in [root/'simulations'/f'node_0{i}' for i in [1,2,3]]+[root.parent/'dashboard']:
 run(['code','--new-window',str(folder)])
meta['vscode_folders']=[str(root/'simulations'/f'node_0{i}') for i in [1,2,3]]+[str(root.parent/'dashboard')];save()
print('STACK BASE STARTED; VS Code folders opened',flush=True)
