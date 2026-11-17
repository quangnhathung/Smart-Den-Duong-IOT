"""Owned RFC2217 reader. Serial receipt time corroborates control, not sensor action time."""
import json,re,time,os
from pathlib import Path
import serial
s=json.loads(Path('/tmp/task010-completion/state.json').read_text());out=Path(s['evidence']);p=serial.serial_for_url('rfc2217://127.0.0.1:4000',baudrate=115200,timeout=.5,do_not_open=True);p.dtr=False;p.rts=False;p.open();buffer=b''
log=(out/'serial.jsonl').open('x',encoding='utf-8',buffering=1);log.write(json.dumps({'event':'start','host_ms':time.time()*1000,'pid':os.getpid(),'note':'RFC2217 read only; no Serial command'})+'\n')
try:
 end=time.monotonic()+1500
 while time.monotonic()<end and not Path('/tmp/task010-completion/stop-serial').exists():
  buffer+=p.read(min(p.in_waiting or 1,8192))
  while b'\n' in buffer:
   line,buffer=buffer.split(b'\n',1);line=line.rstrip(b'\r').decode(errors='replace')
   log.write(json.dumps({'host_ms':time.time()*1000,'monotonic_ns':time.monotonic_ns(),'line':line,'fields':dict(re.findall(r'(\w+)=([^\s]+)',line))},ensure_ascii=False)+'\n')
finally:p.close();log.write(json.dumps({'event':'stop','host_ms':time.time()*1000})+'\n');log.close()
