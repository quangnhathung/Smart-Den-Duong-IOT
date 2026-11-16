"""Read-only RFC2217 sensor corroboration. Serial receive time is not the latency origin."""
import json
import re
import time
from pathlib import Path
from urllib.request import Request, urlopen

import serial

ROOT=Path(__file__).resolve().parent
connection=serial.serial_for_url('rfc2217://127.0.0.1:4000',baudrate=115200,timeout=.5,do_not_open=True)
connection.dtr=False;connection.rts=False
connection.open()
print('Serial read-only observer started; no commands sent',flush=True)
try:
    deadline=time.monotonic()+1200;buffer=b''
    while time.monotonic()<deadline and not (ROOT/'stop-observers.json').exists():
        buffer+=connection.read(min(connection.in_waiting or 1,4096))
        while b'\n' in buffer:
            line,buffer=buffer.split(b'\n',1)
            value=line.rstrip(b'\r').decode(errors='replace')
            if not value.startswith(('SENSORS ','CONTROL ')):continue
            item={'source':'serial','event':'line','observer_ms':time.time()*1000,
                  'line':value,'fields':dict(re.findall(r'(\w+)=([^\s]+)',value))}
            request=Request('http://127.0.0.1:18765/events',data=json.dumps(item).encode(),
                            headers={'Content-Type':'application/json'},method='POST')
            with urlopen(request,timeout=2) as response:response.read()
finally:connection.close()
