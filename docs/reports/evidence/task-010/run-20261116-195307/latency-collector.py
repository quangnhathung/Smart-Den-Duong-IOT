"""Local evidence receiver + real MQTT observer. Does not send commands or modify live DB."""
import json
import socket
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from uuid import uuid4

import paho.mqtt.client as mqtt

ROOT=Path(__file__).resolve().parent
LOCK=threading.RLock()
LATEST={}
TRIAL={}
EVENTS=ROOT/('latency-events-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.jsonl')
stream=EVENTS.open('x',encoding='utf-8',buffering=1)

def record(source,event,**data):
    with LOCK:
        stream.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),
            host_ms=time.time()*1000,perf_ns=time.perf_counter_ns(),source=source,event=event,**data))+'\n')

def on_connect(client,_userdata,_flags,reason,_properties):
    record('mqtt','connect',reason=str(reason))
    if not reason.is_failure:client.subscribe('huit/nhom7/smartlight/v1/node_01/#',qos=0)

def on_message(_client,_userdata,message):
    try:value=json.loads(message.payload)
    except ValueError:value=message.payload.decode(errors='replace')
    with LOCK:
        if message.topic.endswith('/telemetry') and isinstance(value,dict):LATEST.update(value)
        record('mqtt','message',topic=message.topic,body=value,retain=message.retain,qos=message.qos)

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,value):
        raw=json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.send_header('Access-Control-Allow-Origin','http://127.0.0.1:5500')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def do_OPTIONS(self):self.reply(200,{})
    def do_GET(self):
        with LOCK:
            if self.path=='/time':self.reply(200,{'host_ms':time.time()*1000})
            elif self.path=='/state':self.reply(200,{'trial':dict(TRIAL),'latest':dict(LATEST)})
            elif self.path=='/health':self.reply(200,{'status':'OK','events':str(EVENTS)})
            else:self.reply(404,{'error':'not found'})
    def do_POST(self):
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<=65536:self.reply(413,{});return
        try:value=json.loads(self.rfile.read(size))
        except ValueError:self.reply(400,{});return
        with LOCK:
            if self.path=='/trial':
                if not isinstance(value.get('id'),int) or not 1<=value['id']<=10:
                    self.reply(422,{});return
                TRIAL.clear();TRIAL.update(value)
                TRIAL.update(seq_at_arm=str(LATEST.get('seq','0')),boot_at_arm=LATEST.get('boot_id'),
                             armed_host_ms=time.time()*1000)
                record('host','trial-arm',trial=dict(TRIAL))
                self.reply(200,dict(TRIAL))
            elif self.path=='/events':
                if value.get('event')=='trial-ready' and value.get('trial',{}).get('id')==TRIAL.get('id'):
                    TRIAL['browser_ready']=True
                record(value.pop('source','browser'),value.pop('event','observation'),**value)
                self.reply(200,{'host_ms':time.time()*1000})
            else:self.reply(404,{})

class ExclusiveServer(ThreadingHTTPServer):
    allow_reuse_address=False
    def server_bind(self):
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        super().server_bind()

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task010-latency-'+uuid4().hex[:10],clean_session=True)
client.on_connect=on_connect;client.on_message=on_message
server=ExclusiveServer(('127.0.0.1',18765),Handler)
client.connect('127.0.0.1',1883,keepalive=20);client.loop_start()
record('host','start',note='Recorder only; no command publish, sensor fixture or production DB writes')
print('Latency evidence collector http://127.0.0.1:18765',str(EVENTS),flush=True)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:
    server.server_close();client.disconnect();client.loop_stop();record('host','stop');stream.close()
