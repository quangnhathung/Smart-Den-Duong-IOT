"""Bounded read-only RFC2217 capture. No Serial commands, DTR/RTS reset or fault retest."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import serial

path=Path(__file__).resolve().parent/('serial-post-recovery-'+datetime.now().strftime('%H%M%S')+'.jsonl')
with path.open('x',encoding='utf-8',buffering=1) as output:
    def record(event,**value):
        output.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),
                                     perf_ns=time.perf_counter_ns(),event=event,**value))+'\n')
    connection=serial.serial_for_url('rfc2217://127.0.0.1:4000',baudrate=115200,
                                     timeout=.5,do_not_open=True)
    connection.dtr=False
    connection.rts=False
    record('START',seconds=120,serial_commands_sent=0,dtr=False,rts=False)
    try:
        connection.open()
        deadline=time.monotonic()+120
        buffer=b''
        count=0
        while time.monotonic()<deadline:
            buffer+=connection.read(min(connection.in_waiting or 1,4096))
            while b'\n' in buffer:
                line,buffer=buffer.split(b'\n',1)
                record('SERIAL_RX',line=line.rstrip(b'\r').decode('utf-8',errors='replace'))
                count+=1
        if buffer:
            record('SERIAL_PARTIAL',line=buffer.decode('utf-8',errors='replace'))
        record('END',lines=count)
        print('SERIAL_CAPTURED',count,'lines; no commands sent')
    except Exception as error:
        record('ERROR',error=repr(error))
        raise
    finally:
        connection.close()
