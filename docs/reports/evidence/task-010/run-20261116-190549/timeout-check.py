"""Operator-coordinated live TIMEOUT/late-ACK capture. Sends one AUTO through API.

Keep Wokwi running until PAUSE NOW. Pause within 2s, then resume only after
TIMEOUT/RESUME NOW. No mock ACK, database writes, broker changes or automatic retry.
The output is PENDING unless real timeout + late MQTT ACK + DB disposition match.
"""
import json
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx
import paho.mqtt.client as mqtt

ROOT=Path(__file__).resolve().parent
DATABASE=ROOT.parents[4].parent/'Smart-Den-Duong-IOT-BE/data/smartlight.db'
tag=datetime.now().strftime('%Y%m%d-%H%M%S-%f')
output=(ROOT/f'timeout-{tag}.jsonl').open('x',encoding='utf-8',buffering=1)
lock=threading.Lock()
ready=threading.Event()
fresh=threading.Event()
latest={}
acks={}
http=httpx.Client(base_url='http://127.0.0.1:8001',trust_env=False,timeout=5)

def log(event,**data):
    with lock:
        output.write(json.dumps(dict(at=datetime.now(timezone.utc).isoformat(),
                                     perf_ns=time.perf_counter_ns(),event=event,**data))+'\n')

def request(method,path,body=None):
    response=http.request(method,path,json=body) if body is not None else http.request(method,path)
    value=response.json()
    log('HTTP',method=method,path=path,request=body,status=response.status_code,body=value)
    return response.status_code,value

def connected(client,_userdata,_flags,reason,_properties):
    log('MQTT_CONNECT',reason=str(reason))
    if not reason.is_failure:
        client.subscribe('huit/nhom7/smartlight/v1/node_01/#',qos=0)

def subscribed(_client,_userdata,_mid,reasons,_properties):
    log('MQTT_SUBACK',reasons=[str(x) for x in reasons])
    if reasons and all(not x.is_failure for x in reasons):ready.set()

def received(_client,_userdata,message):
    try:value=json.loads(message.payload)
    except ValueError:value=message.payload.decode(errors='replace')
    log('MQTT_MESSAGE',topic=message.topic,body=value,retain=message.retain,qos=message.qos)
    if message.topic.endswith('/telemetry') and isinstance(value,dict):
        latest.update(value)
        fresh.set()
    elif message.topic.endswith('/ack') and isinstance(value,dict):
        acks[value.get('command_id')]=value

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task010-timeout-'+uuid4().hex[:10],
                   clean_session=True,protocol=mqtt.MQTTv311)
client.on_connect=connected
client.on_subscribe=subscribed
client.on_message=received
summary={'result':'PENDING','command_id':None,'scope':'API TIMEOUT and late ACK, not Dashboard rendering'}
started=False
try:
    print('Keep Wokwi RUNNING. Arrange its Pause button and this terminal side by side.',flush=True)
    input('Press ENTER when ready to pause within 2 seconds of PAUSE NOW: ')
    client.connect('127.0.0.1',1883,keepalive=20)
    client.loop_start();started=True
    assert ready.wait(5),'MQTT subscription not ready; no command sent'
    fresh.clear()
    print('Waiting for real fresh telemetry. Do not pause yet.',flush=True)
    assert fresh.wait(45),'No fresh telemetry; no command sent'
    boot=latest['boot_id']
    assert latest['mode']=='AUTO','Expected AUTO initially; no command sent'
    print('PAUSE WOKWI NOW - one AUTO request will be sent in 2 seconds.',flush=True)
    time.sleep(2)
    status,views=request('GET','/api/nodes')
    node=next(x for x in views if x['node_id']=='node_01')
    assert status==200 and node['can_command'] and node['telemetry']['boot_id']==boot,'Not commandable; no command sent'
    sent=time.perf_counter()
    status,command=request('POST','/api/nodes/node_01/commands',{'mode':'AUTO'})
    assert status==202,'Command was not accepted; do not auto-retry'
    identifier=command['command_id'];summary['command_id']=identifier
    print('Command',identifier,'accepted. Keep Wokwi paused until RESUME NOW.',flush=True)
    deadline=time.monotonic()+13
    while command['result']=='PENDING' and time.monotonic()<deadline:
        time.sleep(.2)
        status,command=request('GET','/api/commands/'+identifier)
        assert status==200
    elapsed=time.perf_counter()-sent
    summary.update(final_at_timeout=command,observed_timeout_wall_s=elapsed)
    assert command['result']=='TIMEOUT' and command['reason']=='ACK_TIMEOUT', 'No timeout: pause was missed or transport differed'
    assert elapsed>=9.9,'Timeout observed earlier than expected'
    log('TIMEOUT_CONFIRMED',command_id=identifier,elapsed_s=elapsed)
    print('TIMEOUT confirmed. RESUME WOKWI NOW. Waiting for a real late ACK (up to 90s).',flush=True)
    deadline=time.monotonic()+90
    while identifier not in acks and time.monotonic()<deadline:time.sleep(.1)
    assert identifier in acks,'No real late ACK observed; timeout evidence saved, late ACK still pending'
    assert acks[identifier]['boot_id']==boot,'Firmware boot changed; scenario needs review'
    deadline=time.monotonic()+3
    events=[]
    while time.monotonic()<deadline:
        with sqlite3.connect(DATABASE.as_uri()+'?mode=ro',uri=True) as db:
            db.row_factory=sqlite3.Row
            events=[dict(row) for row in db.execute('SELECT * FROM ack_events WHERE command_id=?',(identifier,))]
        if any(x['disposition']=='LATE_OR_DUPLICATE' for x in events):break
        time.sleep(.1)
    status,final=request('GET','/api/commands/'+identifier)
    assert status==200 and final['result']=='TIMEOUT' and final['reason']=='ACK_TIMEOUT'
    assert any(x['disposition']=='LATE_OR_DUPLICATE' for x in events),'Late ACK disposition not found'
    summary.update(result='PASS',mqtt_late_ack=acks[identifier],ack_events=events,final=final,
                   note='Retry during fresh telemetry and UI result rendering are separate checks.')
    print('PASS: real TIMEOUT, real late ACK, backend remains TIMEOUT. Keep Wokwi running.',flush=True)
except (Exception,KeyboardInterrupt) as error:
    summary['reason']=repr(error)
    log('INCOMPLETE',error=repr(error))
    print('INCOMPLETE:',error,'. RESUME Wokwi if paused. No automatic command retry.',flush=True)
finally:
    log('SUMMARY',**summary)
    with (ROOT/f'timeout-{tag}-summary.json').open('x',encoding='utf-8') as stream:json.dump(summary,stream,indent=2)
    if started:client.disconnect();client.loop_stop()
    http.close();output.close()
    print('Evidence:',ROOT/f'timeout-{tag}-summary.json',flush=True)
