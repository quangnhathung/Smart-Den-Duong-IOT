"""Loopback MQTT test proxy. Delays real ACK frames 12s only when armed by a local file.

No fabricated messages, payload/schema edits, broker ACL changes or DB writes.
Backend must temporarily use SMARTLIGHT_MQTT_PORT=1884; Wokwi stays on1883.
Restore Backend to1883 before stopping this proxy. --seconds is for unattached smoke checks.
"""
import argparse
import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
CONTROL=ROOT/'ack-delay-control.json'
STATUS=ROOT/'ack-delay-status.json'

def publish_parts(frame):
    index=1
    while frame[index]&128:index+=1
    body=frame[index+1:]
    if frame[0]>>4!=3:return None,None
    size=int.from_bytes(body[:2],'big')
    topic=body[2:2+size].decode('utf-8')
    offset=2+size+(2 if (frame[0]>>1)&3 else 0)
    try:value=json.loads(body[offset:])
    except (ValueError,UnicodeDecodeError):value=None
    return topic,value

async def read_frame(reader):
    first=await reader.readexactly(1)
    encoded=bytearray();length=0;multiplier=1
    for _ in range(4):
        digit=(await reader.readexactly(1))[0]
        encoded.append(digit);length+=(digit&127)*multiplier
        if not digit&128:
            if length>65536:raise ValueError('oversized frame; refusing proxy test session')
            return first+encoded+await reader.readexactly(length)
        multiplier*=128
    raise ValueError('invalid MQTT length')

def client_id(frame):
    index=1
    while frame[index]&128:index+=1
    body=frame[index+1:]
    pos=2+int.from_bytes(body[:2],'big')+4
    size=int.from_bytes(body[pos:pos+2],'big')
    return body[pos+2:pos+2+size].decode('utf-8',errors='replace')

class Proxy:
    def __init__(self,log):
        self.log=log;self.clients={};self.targets={};self.used=set();self.server=None

    def record(self,event,**data):
        self.log.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),
                                       perf_ns=time.perf_counter_ns(),event=event,**data))+'\n')

    def status(self):
        value={'at':datetime.now(timezone.utc).isoformat(),'port':1884,
               'backend_clients':[x for x in self.clients.values() if x.startswith('smartlight-backend-')],
               'targets':list(self.targets),'listening':self.server is not None and self.server.is_serving(),
               'log_path':getattr(self.log,'name',None)}
        temporary=STATUS.with_suffix('.tmp')
        try:
            temporary.write_text(json.dumps(value),encoding='utf-8');temporary.replace(STATUS)
        except PermissionError:
            # A status reader can briefly hold the target on Windows. Keep forwarding traffic.
            pass

    async def accept(self,reader,writer):
        peer=str(writer.get_extra_info('peername'));self.clients[peer]='connecting'
        broker_writer=None;tasks=[];delayed=set();send_lock=asyncio.Lock()
        try:
            broker_reader,broker_writer=await asyncio.open_connection('127.0.0.1',1883)
            async def send_client(frame):
                async with send_lock:
                    writer.write(frame);await writer.drain()

            async def release(frame,identifier,deadline):
                await asyncio.sleep(max(0,deadline-time.monotonic()))
                try:
                    await send_client(frame)
                    self.record('REAL_ACK_RELEASED',command_id=identifier,sha256=hashlib.sha256(frame).hexdigest())
                except (ConnectionError,OSError) as error:
                    self.record('REAL_ACK_NOT_DELIVERED',command_id=identifier,error=str(error))

            async def outgoing():
                while True:
                    frame=await read_frame(reader)
                    if frame[0]>>4==1:
                        self.clients[peer]=client_id(frame);self.record('CLIENT_CONNECT',client_id=self.clients[peer])
                    topic,value=publish_parts(frame)
                    if topic=='huit/nhom7/smartlight/v1/node_01/command' and isinstance(value,dict):
                        identifier=value.get('command_id')
                        try:control=json.loads(CONTROL.read_text(encoding='utf-8'))
                        except (OSError,ValueError):control={}
                        nonce=control.get('nonce')
                        if (control.get('arm_next_auto') is True and nonce not in self.used and
                            0<=time.time()-control.get('armed_at',0)<30 and value.get('mode')=='AUTO' and
                            self.clients[peer].startswith('smartlight-backend-')):
                            self.used.add(nonce);self.targets[identifier]=time.monotonic()+12
                            self.record('TARGET_SELECTED',command_id=identifier,delay_s=12,nonce=nonce)
                        self.record('REAL_COMMAND_FORWARDED',command_id=identifier,sha256=hashlib.sha256(frame).hexdigest())
                    broker_writer.write(frame);await broker_writer.drain()

            async def incoming():
                while True:
                    frame=await read_frame(broker_reader)
                    topic,value=publish_parts(frame)
                    identifier=value.get('command_id') if isinstance(value,dict) else None
                    deadline=self.targets.get(identifier,0)
                    if topic=='huit/nhom7/smartlight/v1/node_01/ack' and deadline>time.monotonic():
                        self.record('REAL_ACK_HELD',command_id=identifier,body=value,
                                    sha256=hashlib.sha256(frame).hexdigest(),release_in_s=deadline-time.monotonic())
                        task=asyncio.create_task(release(frame,identifier,deadline))
                        delayed.add(task);task.add_done_callback(delayed.discard)
                    else:
                        await send_client(frame)
            tasks=[asyncio.create_task(outgoing()),asyncio.create_task(incoming())]
            done,_=await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                if not task.cancelled():task.result()
        except (asyncio.IncompleteReadError,ConnectionError,OSError) as error:
            self.record('CONNECTION_END',peer=peer,detail=str(error))
        finally:
            for task in tasks+list(delayed):task.cancel()
            await asyncio.gather(*tasks,*delayed,return_exceptions=True)
            self.clients.pop(peer,None)
            writer.close()
            if broker_writer:broker_writer.close()

    async def run(self,seconds):
        self.server=await asyncio.start_server(self.accept,'127.0.0.1',1884)
        self.record('LISTEN',host='127.0.0.1',port=1884,upstream='127.0.0.1:1883')
        print('MQTT proxy listening on127.0.0.1:1884. Restore Backend to1883 before stopping.',flush=True)
        deadline=time.monotonic()+seconds if seconds else float('inf')
        try:
            async with self.server:
                while time.monotonic()<deadline:self.status();await asyncio.sleep(.25)
        finally:
            self.server.close();await self.server.wait_closed();self.status();self.record('STOP')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds',type=int,default=0)
    args=parser.parse_args()
    filename=ROOT/('ack-delay-proxy-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.jsonl')
    with filename.open('x',encoding='utf-8',buffering=1) as log:
        try:asyncio.run(Proxy(log).run(args.seconds))
        except KeyboardInterrupt:print('Proxy stopped. Backend should use MQTT1883.',flush=True)
