"""Owned TASK-010 QA receiver, real MQTT observer, frame proxy and Wokwi CLI control."""
import asyncio,json,os,queue,signal,subprocess,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
import paho.mqtt.client as mqtt
from proxy import Proxy
from runner import cli_env,CLI
STATE=json.loads(Path('/tmp/task010-completion/state.json').read_text());OUT=Path(STATE['evidence']);ROOT=Path(STATE['root']);LOCK=threading.RLock();LATEST={};STOP=threading.Event();EVENTS=(OUT/'events-v2.jsonl').open('x',encoding='utf-8',buffering=1)
def record(source,event,**data):
 with LOCK:EVENTS.write(json.dumps({'host_ms':time.time()*1000,'monotonic_ns':time.monotonic_ns(),'source':source,'event':event,**data},ensure_ascii=False)+'\n')
class MCP:
 def __init__(self):
  self.env=cli_env();self.index=0;self.pending={};self.lock=threading.Lock();self.proc=subprocess.Popen([str(CLI),'mcp','--quiet',str(ROOT/'simulations/node_01')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=self.env)
  threading.Thread(target=self.reader,daemon=True).start();threading.Thread(target=self.errors,daemon=True).start();self.rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'task010-owned-qa','version':'1'}});self.notify('notifications/initialized')
 def reader(self):
  for line in self.proc.stdout:
   try:v=json.loads(line)
   except ValueError:continue
   q=self.pending.get(v.get('id'))
   if q:q.put(v)
 def errors(self):
  for line in self.proc.stderr:record('cli','stderr',text=line.strip().replace(self.env['WOKWI_CLI_TOKEN'],'<REDACTED>'))
 def notify(self,method):
  with self.lock:self.proc.stdin.write(json.dumps({'jsonrpc':'2.0','method':method})+'\n');self.proc.stdin.flush()
 def rpc(self,method,params,timeout=45):
  with self.lock:
   self.index+=1;identifier=self.index;q=queue.Queue();self.pending[identifier]=q;self.proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':identifier,'method':method,'params':params})+'\n');self.proc.stdin.flush()
  try:return q.get(timeout=timeout)
  finally:self.pending.pop(identifier,None)
 def call(self,name,args):
  begin=time.time()*1000;result=self.rpc('tools/call',{'name':name,'arguments':args});end=time.time()*1000;record('cli','tool_result',name=name,arguments=args,begin_ms=begin,end_ms=end,result=result);return {'begin_ms':begin,'end_ms':end,'response':result}
 def close(self):
  try:self.call('wokwi_stop_simulation',{})
  except Exception:pass
  if self.proc.poll() is None:self.proc.terminate()
  try:self.proc.wait(timeout=3)
  except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
mcp=MCP();loop=asyncio.new_event_loop();proxy=Proxy(record)
def proxy_thread():
 asyncio.set_event_loop(loop)
 async def start():
  for port in [1883,11883]:await asyncio.start_server(proxy.accept,'127.0.0.1',port)
 loop.run_until_complete(start());loop.run_forever()
threading.Thread(target=proxy_thread,daemon=True).start()
def on_connect(client,userdata,flags,reason,props):
 record('mqtt','connect',reason=str(reason))
 if not reason.is_failure:client.subscribe('huit/nhom7/smartlight/v1/node_01/#',qos=0)
def on_message(client,userdata,message):
 try:body=json.loads(message.payload)
 except ValueError:body=message.payload.decode(errors='replace')
 if message.topic.endswith('/telemetry') and isinstance(body,dict):
  with LOCK:LATEST.clear();LATEST.update(body)
 record('mqtt','message',topic=message.topic,body=body,retain=message.retain,qos=message.qos)
client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task010-observer-'+uuid.uuid4().hex[:10],clean_session=True);client.on_connect=on_connect;client.on_message=on_message;client.connect_async('127.0.0.1',11884,20);client.loop_start()
def poll():
 while not STOP.is_set():
  for path in ['health','nodes']:
   try:
    with urlopen('http://127.0.0.1:8001/api/'+path,timeout=1) as r:value=json.loads(r.read());status=r.status
    record('api','poll',path=path,status=status,body=value)
   except Exception as e:record('api','unavailable',path=path,error=type(e).__name__)
  STOP.wait(1)
threading.Thread(target=poll,daemon=True).start()
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,status,value):
  raw=json.dumps(value,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(raw)));self.send_header('Access-Control-Allow-Origin','http://127.0.0.1:5500');self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS');self.send_header('Access-Control-Allow-Headers','Content-Type');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
 def do_OPTIONS(self):self.reply(200,{})
 def do_GET(self):
  if self.path=='/state':
   with LOCK:latest=dict(LATEST)
   self.reply(200,{'latest':latest,'proxy':proxy.state(),'host_ms':time.time()*1000,'mcp_pid':mcp.proc.pid})
  elif self.path=='/time':self.reply(200,{'host_ms':time.time()*1000})
  else:self.reply(404,{})
 def do_POST(self):
  try:
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=131072:raise ValueError('Invalid event size')
   value=json.loads(self.rfile.read(size))
   if self.path=='/events':record('browser',value.pop('event','observation'),**value);self.reply(200,{'host_ms':time.time()*1000})
   elif self.path=='/proxy':proxy.arm(value['mode']);self.reply(200,proxy.state())
   elif self.path=='/mcp':
    allowed=['wokwi_start_simulation','wokwi_stop_simulation','wokwi_get_status','wokwi_read_serial','wokwi_set_control','wokwi_write_serial']
    if value['name'] not in allowed:raise ValueError('Unknown QA tool')
    self.reply(200,mcp.call(value['name'],value.get('arguments',{})))
   elif self.path=='/stop':self.reply(200,{'stopping':True});STOP.set();threading.Thread(target=server.shutdown,daemon=True).start()
   else:self.reply(404,{})
  except Exception as e:self.reply(500,{'error':type(e).__name__,'message':str(e)[:180]});record('controller','request_error',error=type(e).__name__)
server=ThreadingHTTPServer(('127.0.0.1',18765),Handler);record('controller','start',pid=os.getpid());print('Owned QA controller ready 18765',flush=True)
try:server.serve_forever(poll_interval=.2)
finally:
 STOP.set();server.server_close();mcp.close();client.disconnect();client.loop_stop();record('controller','stop')
