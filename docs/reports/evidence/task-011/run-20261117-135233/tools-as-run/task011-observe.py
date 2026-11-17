import json,time,threading,signal,sys
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import paho.mqtt.client as mqtt
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);LOCK=threading.RLock();LATEST={};EVENTS=[]
log=(OUT/'mqtt-events-fast.jsonl').open('w',buffering=1)
def record(event,**data):
    with LOCK:
        v={'event':event,'host_ms':time.time()*1000,'monotonic_ns':time.monotonic_ns(),**data};EVENTS.append(v);log.write(json.dumps(v)+'\n')
def connected(client,userdata,flags,reason,properties):
    record('connected',reason=str(reason));client.subscribe('huit/nhom7/smartlight/v1/#',1)
def disconnected(client,userdata,flags,reason,properties):record('disconnected',reason=str(reason))
def message(client,userdata,msg):
    try:payload=json.loads(msg.payload)
    except ValueError:payload=msg.payload.decode(errors='replace')
    record('mqtt',topic=msg.topic,payload=payload,retain=msg.retain,qos=msg.qos)
    if msg.topic.endswith('/telemetry') and isinstance(payload,dict):
        with LOCK:LATEST[payload['node_id']]={'payload':payload,'host_ms':time.time()*1000}
client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task011-observer-fast');client.reconnect_delay_set(min_delay=1,max_delay=2);client.on_connect=connected;client.on_disconnect=disconnected;client.on_message=message;client.connect('127.0.0.1',1883,20);client.loop_start()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def do_GET(self):
        with LOCK:
            value={'latest':LATEST,'events_count':len(EVENTS),'connected':client.is_connected()} if self.path=='/state' else EVENTS[max(0,int(self.path.split('=')[-1])):]
            raw=json.dumps(value).encode()
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',18771),Handler)
signal.signal(signal.SIGTERM,lambda *a:sys.exit(0))
try:server.serve_forever()
finally:client.disconnect();client.loop_stop();server.server_close();log.close()
