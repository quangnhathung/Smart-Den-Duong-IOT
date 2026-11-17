import json,threading,time,signal,sys
from pathlib import Path
import serial
s=json.loads(Path('/tmp/task011-active.json').read_text());out=Path(s['evidence']);lock=threading.Lock();log=(out/'serial-events-cpu4.jsonl').open('a',buffering=1);stop=threading.Event()
def observe(index):
    port=serial.serial_for_url(f'rfc2217://127.0.0.1:{3999+index}',baudrate=115200,timeout=.3,do_not_open=True)
    port.dtr=False;port.rts=False;port.open()
    with port:
        pending=b''
        while not stop.is_set():
            pending+=port.read(512)
            lines=pending.split(b'\n');pending=lines.pop()
            for line in lines:
                with lock:log.write(json.dumps({'node_id':f'node_0{index}','port':3999+index,'host_ms':time.time()*1000,'monotonic_ns':time.monotonic_ns(),'line':line.decode(errors='replace').strip()})+'\n')
for i in (1,2,3):threading.Thread(target=observe,args=(i,),daemon=True).start()
signal.signal(signal.SIGTERM,lambda *a:stop.set())
while not stop.wait(1):pass
log.close()
