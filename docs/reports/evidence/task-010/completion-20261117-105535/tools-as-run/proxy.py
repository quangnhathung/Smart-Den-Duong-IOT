"""QA-only MQTT frame proxy; all traffic passes unchanged except an explicitly armed test."""
import asyncio,hashlib,json,time

def encode_remaining(size):
 result=bytearray()
 while True:
  value=size%128;size//=128;result.append(value|(128 if size else 0))
  if not size:return bytes(result)
def body_offset(frame):
 index=1
 for _ in range(4):
  value=frame[index];index+=1
  if not value&128:return index
 raise ValueError('Invalid remaining length')
def publish(frame):
 if frame[0]>>4!=3:return None
 offset=body_offset(frame);size=int.from_bytes(frame[offset:offset+2],'big');topic=frame[offset+2:offset+2+size].decode()
 payload=offset+2+size+(2 if frame[0]&6 else 0)
 try:value=json.loads(frame[payload:])
 except (UnicodeDecodeError,ValueError):value=None
 return topic,value,payload
def replace_payload(frame,value):
 _,_,offset=publish(frame);start=body_offset(frame);body=frame[start:offset]+json.dumps(value,separators=(',',':')).encode()
 return frame[:1]+encode_remaining(len(body))+body
def connect_id(frame):
 if frame[0]>>4!=1:return None
 offset=body_offset(frame);protocol=int.from_bytes(frame[offset:offset+2],'big');offset+=2+protocol+4;size=int.from_bytes(frame[offset:offset+2],'big');return frame[offset+2:offset+2+size].decode()
async def read_frame(reader):
 first=await reader.readexactly(1);encoded=bytearray();size=0;mult=1
 for _ in range(4):
  value=(await reader.readexactly(1))[0];encoded.append(value);size+=(value&127)*mult
  if not value&128:
   if size>65536:raise ValueError('Oversized MQTT frame')
   return first+encoded+await reader.readexactly(size)
  mult*=128
 raise ValueError('Invalid MQTT length')
class Proxy:
 def __init__(self,record,upstream_port=11884):self.record=record;self.port=upstream_port;self.mode='passthrough';self.target=None;self.started=0;self.connections={};self.tasks=set()
 def arm(self,mode):
  if mode not in ['passthrough','expired','hold_ack','drop_ack']:raise ValueError('Unknown QA proxy mode')
  self.mode=mode;self.target=None;self.started=0;self.record('proxy','arm',mode=mode)
 def state(self):return {'mode':self.mode,'target':self.target,'clients':list(self.connections.values())}
 async def accept(self,reader,writer):
  peer=str(writer.get_extra_info('peername'));upstream=None;tasks=[];self.connections[peer]='connecting'
  try:
   other_reader,upstream=await asyncio.open_connection('127.0.0.1',self.port)
   lock=asyncio.Lock()
   async def send_up(frame):
    async with lock:upstream.write(frame);await upstream.drain()
   async def delayed(frame,identifier,when):
    await asyncio.sleep(max(0,when-time.monotonic()))
    try:await send_up(frame);self.record('proxy','ack_released',command_id=identifier,sha256=hashlib.sha256(frame).hexdigest())
    except (OSError,ConnectionError):self.record('proxy','ack_discarded_on_disconnect',command_id=identifier)
   async def to_broker():
    while True:
     frame=await read_frame(reader);identifier=connect_id(frame)
     if identifier:self.connections[peer]=identifier;self.record('proxy','connect',client_id=identifier)
     item=publish(frame)
     if item:
      topic,value,_=item;digest=hashlib.sha256(frame).hexdigest();self.record('proxy','publish',direction='client_to_broker',client_id=self.connections[peer],topic=topic,body=value,sha256=digest)
      if topic == 'huit/nhom7/smartlight/v1/node_01/command' and isinstance(value,dict) and self.mode!='passthrough' and self.target is None:
       self.target=value.get('command_id');self.started=time.monotonic();self.record('proxy','target_selected',mode=self.mode,command_id=self.target)
      if topic == 'huit/nhom7/smartlight/v1/node_01/command' and self.mode=='expired' and value.get('command_id')==self.target:
       value={**value,'deadline_uptime_ms':0};modified=replace_payload(frame,value);self.record('proxy','expired_fault_injection',command_id=self.target,original_sha256=digest,modified_sha256=hashlib.sha256(modified).hexdigest(),body=value);frame=modified
      if topic.endswith('/ack') and isinstance(value,dict) and value.get('command_id')==self.target and self.mode in ['hold_ack','drop_ack']:
       self.record('proxy','real_ack_held',mode=self.mode,command_id=self.target,body=value,sha256=digest)
       if self.mode=='hold_ack':
        task=asyncio.create_task(delayed(frame,self.target,self.started+12));self.tasks.add(task);task.add_done_callback(self.tasks.discard)
       continue
     await send_up(frame)
   async def from_broker():
    while True:
     frame=await read_frame(other_reader);writer.write(frame);await writer.drain()
   tasks=[asyncio.create_task(to_broker()),asyncio.create_task(from_broker())];await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
  except (OSError,ConnectionError,asyncio.IncompleteReadError,ValueError) as error:self.record('proxy','connection_end',client_id=self.connections.get(peer),reason=type(error).__name__)
  finally:
   for task in tasks:task.cancel()
   if tasks:await asyncio.gather(*tasks,return_exceptions=True)
   if upstream:upstream.close()
   writer.close();self.connections.pop(peer,None)
