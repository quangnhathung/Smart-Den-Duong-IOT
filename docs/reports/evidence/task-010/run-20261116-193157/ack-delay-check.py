"""Automatic live TIMEOUT/late-ACK check via the armed real-frame delay proxy.

Requires Backend routed through local1884 and real Wokwi running on broker1883.
Sends one AUTO immediately after fresh telemetry; proxy delays actual ACKs12s.
No Pause/Resume race, fabricated ACKs, direct DB writes or automatic POST retry.
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
output=(ROOT/f'ack-delay-check-{tag}.jsonl').open('x',encoding='utf-8',buffering=1)
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

client=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='task010-ack-observer-'+uuid4().hex[:10],
                   clean_session=True,protocol=mqtt.MQTTv311)
client.on_connect=connected
client.on_subscribe=subscribed
client.on_message=received
summary={'result':'PENDING','command_id':None,'scope':'Real ACK transport-delay injection; not Dashboard rendering'}
started=False
try:
    proxy=json.loads((ROOT/'ack-delay-status.json').read_text(encoding='utf-8'))
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(proxy['at'])).total_seconds()
    assert age<3 and proxy['listening'] and len(proxy['backend_clients'])==1,'Backend must be connected through proxy1884; no command sent'
    print('Keep Wokwi RUNNING. Real ACK delay is automatic; do not Pause.',flush=True)
    client.connect('127.0.0.1',1883,keepalive=20)
    client.loop_start();started=True
    assert ready.wait(5),'MQTT subscription not ready; no command sent'
    fresh.clear()
    print('Waiting for real fresh telemetry. Do not pause yet.',flush=True)
    assert fresh.wait(45),'No fresh telemetry; no command sent'
    boot=latest['boot_id']
    assert latest['mode']=='AUTO','Expected AUTO initially; no command sent'
    # The direct broker observer can see a sample milliseconds before the proxied collector.
    # Wait for that exact fresh sample at the API; this retries GET only, never POST.
    expected_seq=int(latest['seq'])
    catchup_deadline=time.monotonic()+1.5
    while True:
        status,views=request('GET','/api/nodes')
        node=next(x for x in views if x['node_id']=='node_01')
        if (status==200 and node['can_command'] and node['telemetry']['boot_id']==boot and
            int(node['telemetry']['seq'])>=expected_seq):break
        assert time.monotonic()<catchup_deadline,'Fresh sample did not reach API; no command sent'
        time.sleep(.05)
    control={'arm_next_auto':True,'nonce':uuid4().hex,'armed_at':time.time()}
    temporary=ROOT/'ack-delay-control.tmp'
    temporary.write_text(json.dumps(control),encoding='utf-8')
    temporary.replace(ROOT/'ack-delay-control.json')
    log('PROXY_ARMED',**control)
    sent=time.perf_counter()
    status,command=request('POST','/api/nodes/node_01/commands',{'mode':'AUTO'})
    assert status==202,'Command was not accepted; do not auto-retry'
    identifier=command['command_id'];summary['command_id']=identifier
    print('Command',identifier,'accepted. Proxy holds real ACKs12s; telemetry continues.',flush=True)
    deadline=time.monotonic()+13
    while command['result']=='PENDING' and time.monotonic()<deadline:
        time.sleep(.2)
        status,command=request('GET','/api/commands/'+identifier)
        assert status==200
    elapsed=time.perf_counter()-sent
    summary.update(final_at_timeout=command,observed_timeout_wall_s=elapsed)
    assert command['result']=='TIMEOUT' and command['reason']=='ACK_TIMEOUT', 'No timeout observed; inspect actual proxy selection/hold log, do not retry automatically'
    assert elapsed>=9.9,'Timeout observed earlier than expected'
    log('TIMEOUT_CONFIRMED',command_id=identifier,elapsed_s=elapsed)
    print('TIMEOUT confirmed. Waiting for proxy to release real ACKs; do not alter Wokwi.',flush=True)
    deadline=time.monotonic()+20
    while identifier not in acks and time.monotonic()<deadline:time.sleep(.1)
    assert identifier in acks,'No real late ACK observed; timeout evidence saved, late ACK still pending'
    assert acks[identifier]['boot_id']==boot,'Firmware boot changed; scenario needs review'
    deadline=time.monotonic()+8
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
    proxy=json.loads((ROOT/'ack-delay-status.json').read_text(encoding='utf-8'))
    assert identifier in proxy['targets'],'Proxy did not select this exact command ID'
    proxy_path=Path(proxy['log_path']).resolve()
    assert proxy_path.parent==ROOT,'Proxy log path must stay in this evidence directory'
    proxy_events=[]
    for line in proxy_path.read_text(encoding='utf-8').splitlines():
        try:item=json.loads(line)
        except ValueError:continue
        if item.get('command_id')==identifier:proxy_events.append(item)
    selected=next(x for x in proxy_events if x['event']=='TARGET_SELECTED')
    held=[x for x in proxy_events if x['event']=='REAL_ACK_HELD']
    released=[x for x in proxy_events if x['event']=='REAL_ACK_RELEASED']
    assert held and released and {x['sha256'] for x in held}&{x['sha256'] for x in released},'No unchanged held/released real ACK frame'
    assert min(x['perf_ns'] for x in released)-selected['perf_ns']>=11.9e9,'ACK released before intended test delay'
    summary.update(result='PASS',mqtt_ack_seen_at_broker=acks[identifier],ack_events=events,final=final,
                   proxy_log=str(proxy_path),proxy_events=proxy_events,
                   note='ACK seen timely at broker; arrival at Backend intentionally delayed. Check proxy raw-frame hashes/timestamps. UI rendering separate.')
    print('PASS: real TIMEOUT and real delayed ACK; backend remains TIMEOUT. Restore Backend MQTT1883 before stopping proxy.',flush=True)
except (Exception,KeyboardInterrupt) as error:
    summary['reason']=repr(error)
    log('INCOMPLETE',error=repr(error))
    print('INCOMPLETE:',error,'. No automatic retry. Restore Backend MQTT1883 before stopping proxy.',flush=True)
finally:
    if 'control' in globals():
        try:
            path=ROOT/'ack-delay-control.json'
            active=json.loads(path.read_text(encoding='utf-8'))
            if active.get('nonce')==control['nonce']:
                active['arm_next_auto']=False
                temporary=ROOT/'ack-delay-control.tmp'
                temporary.write_text(json.dumps(active),encoding='utf-8');temporary.replace(path)
        except (OSError,ValueError) as error:log('DISARM_ERROR',error=repr(error))
    log('SUMMARY',**summary)
    with (ROOT/f'ack-delay-check-{tag}-summary.json').open('x',encoding='utf-8') as stream:json.dump(summary,stream,indent=2)
    if started:client.disconnect();client.loop_stop()
    http.close();output.close()
    print('Evidence:',ROOT/f'ack-delay-check-{tag}-summary.json',flush=True)
