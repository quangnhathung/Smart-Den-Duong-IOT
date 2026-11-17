import asyncio,json,unittest
from proxy import encode_remaining,body_offset,publish,replace_payload,connect_id,read_frame,Proxy

def pub(topic,value,qos=0):
 name=topic.encode();body=len(name).to_bytes(2,'big')+name+(b'\x00\x07' if qos else b'')+json.dumps(value).encode();return bytes([0x30|(qos<<1)])+encode_remaining(len(body))+body
class ProxyChecks(unittest.TestCase):
 def test_qos_and_multibyte_payload_are_preserved(self):
  for qos in [0,1,2]:
   original=pub('huit/nhom7/smartlight/v1/node_01/command',{'command_id':'a','deadline_uptime_ms':123,'note':'x'*180},qos);updated=replace_payload(original,{'command_id':'a','deadline_uptime_ms':0})
   self.assertEqual(updated[0],original[0]);self.assertEqual(publish(updated)[1]['deadline_uptime_ms'],0)
   a=body_offset(original);b=body_offset(updated);self.assertEqual(original[a:publish(original)[2]],updated[b:publish(updated)[2]])
 def test_connect_client_identity(self):
  body=b'\x00\x04MQTT\x04\x02\x00\x14\x00\x04test';frame=b'\x10'+encode_remaining(len(body))+body;self.assertEqual(connect_id(frame),'test');self.assertIsNone(connect_id(b'\xc0\x00'))
 def test_fragmented_stream_and_size_limit(self):
  async def run():
   frame=pub('node/telemetry',{'seq':1});reader=asyncio.StreamReader()
   task=asyncio.create_task(read_frame(reader))
   for byte in frame:reader.feed_data(bytes([byte]));await asyncio.sleep(0)
   self.assertEqual(await task,frame)
   reader=asyncio.StreamReader();reader.feed_data(b'\x30'+encode_remaining(65537))
   with self.assertRaises(ValueError):await read_frame(reader)
  asyncio.run(run())
 def test_forward_hold_release_and_drop_use_real_bytes(self):
  async def run():
   log=[];received=[]
   async def broker(reader,writer):
    try:
     while True:received.append(await read_frame(reader))
    except asyncio.IncompleteReadError:pass
    finally:writer.close()
   upstream=await asyncio.start_server(broker,'127.0.0.1',0)
   proxy=Proxy(lambda *a,**kw:log.append((a,kw)),upstream.sockets[0].getsockname()[1]);front=await asyncio.start_server(proxy.accept,'127.0.0.1',0)
   reader,writer=await asyncio.open_connection('127.0.0.1',front.sockets[0].getsockname()[1])
   try:
    command=pub('huit/nhom7/smartlight/v1/node_01/command',{'command_id':'a','deadline_uptime_ms':5},1);ack=pub('node/ack',{'command_id':'a','result':'APPLIED'})
    proxy.arm('expired');writer.write(command);await writer.drain();await asyncio.sleep(.02);self.assertEqual(publish(received[-1])[1]['deadline_uptime_ms'],0)
    proxy.arm('hold_ack');writer.write(command);await writer.drain();await asyncio.sleep(.02);proxy.started-=12
    writer.write(ack);await writer.drain();await asyncio.sleep(.02);self.assertEqual(received[-1],ack)
    proxy.arm('drop_ack');writer.write(command+ack);await writer.drain();await asyncio.sleep(.02);self.assertEqual(received[-1],command)
    proxy.arm('passthrough');writer.write(ack);await writer.drain();await asyncio.sleep(.02);self.assertEqual(received[-1],ack)
   finally:
    writer.close();await writer.wait_closed();front.close();upstream.close();await front.wait_closed();await upstream.wait_closed()
  asyncio.run(run())
if __name__=='__main__':unittest.main()
