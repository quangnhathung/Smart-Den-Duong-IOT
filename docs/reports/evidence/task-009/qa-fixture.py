"""QA ONLY: actual FastAPI/SQLite with synthetic clocked MQTT events, no broker connections."""
from pathlib import Path
import json,sys,threading,time,uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[5]/'backend'))
from smartlight.api import create_app
from smartlight.config import Settings
from smartlight.engine import Engine
from smartlight.models import ExperimentInput,PREFIX
import uvicorn
ROOT=Path('/tmp/task009-browser-fixture-'+uuid.uuid4().hex[:8]+'.db')
NODES=['node_01','node_02']
def telemetry(node,seq,uptime,mode='AUTO',applied=None):
    if applied is None:applied=25 if node=='node_01' else 70
    fault=node=='node_02'
    return dict(schema_version=1,node_id=node,boot_id='b7e28a10' if node=='node_01' else 'b7e28a11',seq=seq,uptime_ms=uptime,mode=mode,environment='NIGHT',ldr_adc=3100 if not fault else 2800,motion='NONE' if not fault else 'PEDESTRIAN',distance_cm=150.0,brightness_target=applied,brightness_applied=applied,current_adc=0 if fault else 4095,current_ma_sim=0.0 if fault else 2000.0*applied/100,power_sim_w=0.0 if fault else 24.0*applied/100,faults=['OPEN_LOAD'] if fault else [])
def avail(node):return dict(schema_version=1,node_id=node,boot_id='b7e28a10' if node=='node_01' else 'b7e28a11',status='ONLINE')
class SeedClock:
    wall=time.time()-600
    value=0
    def utc(self):return self.wall+self.value
    def mono(self):return self.value
class Transport:
    connected=True
    session='fixture-live'
    def __init__(self):self.sink=None;self.stop_event=threading.Event();self.start_time=time.monotonic();self.values={n:{'mode':'AUTO','brightness':25 if n=='node_01' else 70} for n in NODES};self.seq=301
    def start(self,sink):
        self.sink=sink
        for n in NODES:sink(f'{PREFIX}/{n}/availability',json.dumps(avail(n)).encode(),self.session)
        self.thread=threading.Thread(target=self.run,daemon=True);self.thread.start()
    def run(self):
        while not self.stop_event.is_set():
            for n in NODES:
                v=self.values[n]
                self.sink(f'{PREFIX}/{n}/telemetry',json.dumps(telemetry(n,self.seq,3600000+int((time.monotonic()-self.start_time)*1000),v['mode'],v['brightness'])).encode(),self.session)
            self.seq+=1;self.stop_event.wait(.7)
    def stop(self):self.connected=False;self.stop_event.set();getattr(self,'thread',threading.current_thread()).join(2)
    def publish(self,topic,payload,session):
        command=json.loads(payload);node=command['node_id'];self.values[node]={'mode':command['mode'],'brightness':command.get('brightness',25 if node=='node_01' else 70)}
        ack=dict(schema_version=1,node_id=node,boot_id=command['boot_id'],command_id=command['command_id'],result='APPLIED',reason=None)
        threading.Timer(.15,lambda:self.sink(f'{PREFIX}/{node}/ack',json.dumps(ack).encode(),self.session)).start();return True
transport=Transport();clock=SeedClock();engine=Engine(ROOT,transport,clock);engine.connection(True,transport.session)
for n in NODES:engine.ingest(f'{PREFIX}/{n}/availability',json.dumps(avail(n)).encode())
exp=engine.reporting.start_experiment(ExperimentInput(name='EX-02 · Bộ kiểm tra giả lập',configuration={'source':'synthetic QA fixture'},notes='Dữ liệu kiểm thử giao diện; không phải kết quả Wokwi.'))
for i in range(300):
    clock.value=i*2
    for n in NODES:engine.ingest(f'{PREFIX}/{n}/telemetry',json.dumps(telemetry(n,i,3000000+i*2000,applied=(25 if i%60<40 else 100) if n=='node_01' else 70)).encode())
engine.reporting.stop_experiment(exp['id']);engine.close()
print('QA fixture only; database',ROOT,flush=True)
app=create_app(Settings(database=ROOT),transport)
uvicorn.run(app,host='127.0.0.1',port=8000,log_level='warning')
