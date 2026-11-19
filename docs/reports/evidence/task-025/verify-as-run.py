import json,time,urllib.request,subprocess,datetime
from pathlib import Path
import paho.mqtt.client as mqtt
root=Path('/home/quangnhathung/HungQuang_WorkSpace/Learing/Iot/DoAn/firmware')
out=root/'docs/reports/evidence/task-025'
def get(path):
 with urllib.request.urlopen('http://127.0.0.1:8000'+path,timeout=5) as r:return json.load(r)
messages=[]
c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task025-readonly-probe')
def connected(client,userdata,flags,rc,properties):client.subscribe('huit/nhom7/smartlight/v1/+/telemetry')
def received(client,userdata,msg):messages.append({'at':datetime.datetime.now().astimezone().isoformat(),'topic':msg.topic,'payload':json.loads(msg.payload)})
c.on_connect=connected;c.on_message=received;c.connect('127.0.0.1',1883);c.loop_start()
first=get('/api/nodes');deadline=time.monotonic()+15
while time.monotonic()<deadline:
 counts={n:sum(m['topic'].split('/')[-2]==n for m in messages) for n in ['node_01','node_02','node_03']}
 if all(v>=2 for v in counts.values()):break
 time.sleep(.25)
c.disconnect();c.loop_stop()
last=get('/api/nodes');health=get('/api/health')
with urllib.request.urlopen('http://127.0.0.1:5500/',timeout=5) as r:frontend={'status':r.status,'contains_dashboard':b'<html' in r.read().lower()}
proof={'at':datetime.datetime.now().astimezone().isoformat(),'health':health,'first_nodes':first,'last_nodes':last,'mqtt_counts':counts,'messages':messages,'frontend':frontend,'listeners':subprocess.check_output(['ss','-ltnp'],text=True),'broker_logs':subprocess.check_output(['docker','compose','-f',str(root/'infra/compose.yaml'),'logs','--tail=30','mosquitto'],text=True)}
(out/'runtime.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
assert health['status']=='OK' and health['dropped_events']==0
assert len(last)==3 and all(n['connection']=='ONLINE' and n['freshness']=='FRESH' for n in last)
assert all(v>=2 for v in counts.values())
assert frontend['status']==200 and frontend['contains_dashboard']
print(json.dumps({'at':proof['at'],'health':health,'mqtt_counts':counts,'nodes':[{k:n.get(k) for k in ['node_id','connection','freshness','age_s']} for n in last],'frontend':frontend},ensure_ascii=False))
