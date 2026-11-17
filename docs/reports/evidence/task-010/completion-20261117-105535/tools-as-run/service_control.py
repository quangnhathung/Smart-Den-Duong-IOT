"""Control only the explicitly owned TASK-010 QA backend and broker."""
import json,os,signal,subprocess,threading,time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
S=json.loads(Path('/tmp/task010-completion/state.json').read_text());ROOT=Path(S['root']);OUT=Path(S['evidence']);WORK=Path('/tmp/task010-completion');BROKER=json.loads((OUT/'owned-broker.json').read_text())['name'];CURRENT=json.loads((OUT/'owned-backend.json').read_text())['pid'];LOG=(OUT/'service-actions.jsonl').open('x',buffering=1)
def record(event,**kw):LOG.write(json.dumps({'host_ms':time.time()*1000,'event':event,**kw})+'\n')
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def reply(self,status,v):
  data=json.dumps(v).encode();self.send_response(status);self.send_header('Content-Length',str(len(data)));self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
 def do_POST(self):
  global CURRENT
  try:
   begin=time.time()*1000
   if self.path=='/backend/restart':
    old=CURRENT;cmd=Path(f'/proc/{old}/cmdline').read_bytes();env=Path(f'/proc/{old}/environ').read_bytes();assert b'uvicorn' in cmd and ('SMARTLIGHT_DB='+str(WORK/'qa.db')).encode()+b'\0' in env
    record('backend_stop',pid=old);os.kill(old,signal.SIGINT);end=time.monotonic()+6
    while time.monotonic()<end and Path(f'/proc/{old}').exists():
     if 'State:\tZ' in Path(f'/proc/{old}/status').read_text():break
     time.sleep(.05)
    settings=dict(os.environ);settings.update(SMARTLIGHT_DB=str(WORK/'qa.db'),SMARTLIGHT_MQTT_HOST='127.0.0.1',SMARTLIGHT_MQTT_PORT='11883')
    log=(OUT/('backend-restarted-'+str(int(time.time()))+'.log')).open('x');p=subprocess.Popen([str(ROOT.parent/'backend/.venv/bin/python'),'-B','-m','uvicorn','smartlight.api:app','--host','127.0.0.1','--port','8001','--workers','1'],cwd=ROOT.parent/'backend',env=settings,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);CURRENT=p.pid;record('backend_start',old_pid=old,pid=CURRENT);(WORK/'current-backend.json').write_text(json.dumps({'pid':CURRENT}))
    result={'old_pid':old,'new_pid':CURRENT}
   elif self.path in ['/broker/stop','/broker/start']:
    label=subprocess.run(['docker','inspect','--format','{{index .Config.Labels "smartlight.qa"}}',BROKER],check=True,capture_output=True,text=True).stdout.strip();assert label==OUT.name
    action=self.path.rsplit('/',1)[1];record('broker_'+action,container=BROKER)
    subprocess.run(['docker',action,BROKER],check=True,capture_output=True,text=True);result={'container':BROKER,'action':action}
   elif self.path=='/stop':self.reply(200,{'stopping':True});threading.Thread(target=server.shutdown,daemon=True).start();return
   else:self.reply(404,{});return
   self.reply(200,{'begin_ms':begin,'end_ms':time.time()*1000,**result})
  except Exception as e:record('error',error=type(e).__name__,message=str(e));self.reply(500,{'error':type(e).__name__})
server=ThreadingHTTPServer(('127.0.0.1',18766),Handler);record('start',pid=os.getpid())
try:server.serve_forever()
finally:server.server_close();record('stop');LOG.close()
