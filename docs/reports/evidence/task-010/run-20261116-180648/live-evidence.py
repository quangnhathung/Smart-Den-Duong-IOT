"""TASK-010 live evidence. No fixture, direct DB writes, service kills or schema changes.

Run with backend .venv Python. Output is exclusive-create, one phase per invocation.
run creates/stops its own experiment and sends 10 alternating commands for latency.
capture only subscribes/polls. snapshot reads SQLite in a read-only transaction.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import platform
import sqlite3
import statistics
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx
import paho.mqtt.client as mqtt

ROOT = Path(__file__).resolve().parent
FIRMWARE = ROOT.parents[4]
BACKEND = FIRMWARE.parent / 'Smart-Den-Duong-IOT-BE'
PREFIX = 'huit/nhom7/smartlight/v1/node_01'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('phase', choices=['snapshot', 'run', 'capture', 'reject', 'cache', 'pending', 'experiment-export'])
parser.add_argument('--tag', default=datetime.now().strftime('%Y%m%d-%H%M%S'))
parser.add_argument('--seconds', type=int, default=180)
parser.add_argument('--experiment-id', type=int)
args = parser.parse_args()
logfile = (ROOT / f'{args.phase}-{args.tag}.jsonl').open('x', encoding='utf-8', buffering=1)
mutex = threading.Lock()
http = httpx.Client(base_url='http://127.0.0.1:8001', timeout=5, trust_env=False)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def log(event, **data):
    with mutex:
        logfile.write(json.dumps(dict(at=stamp(), perf_ns=time.perf_counter_ns(),
                                      event=event, **data), ensure_ascii=False) + '\n')


def save(name, value):
    with (ROOT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)


def api(method, path, body=None):
    start = time.perf_counter_ns()
    response = http.request(method, path, json=body) if body is not None else http.request(method, path)
    try:
        value = response.json()
    except ValueError:
        value = response.text
    log('HTTP', method=method, path=path, request=body, status=response.status_code,
        elapsed_ms=(time.perf_counter_ns()-start)/1e6, body=value,
        content_type=response.headers.get('content-type'))
    return response.status_code, value


def db_snapshot(tag):
    path = BACKEND / 'data/smartlight.db'
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        tables = {}
        for name in ['telemetry', 'commands', 'ack_events', 'alerts', 'experiments', 'availability']:
            tables[name] = [dict(row) for row in db.execute(f'SELECT * FROM {name}')]
        info = dict(at=stamp(), db=str(path), sqlite=sqlite3.sqlite_version,
                    integrity=[row[0] for row in db.execute('PRAGMA quick_check')],
                    schema_version=db.execute('PRAGMA user_version').fetchone()[0], tables=tables)
        db.rollback()
    save(f'sqlite-{tag}.json', info)
    log('SQLITE_SNAPSHOT', tag=tag, counts={name:len(rows) for name, rows in tables.items()},
        integrity=info['integrity'])
    for command in tables['commands']:
        api('GET', '/api/commands/' + command['command_id'])
    return info


ready = threading.Event()
acks = {}
messages = []


def connect(client, _userdata, _flags, reason, _properties):
    log('MQTT_CONNECT', reason=str(reason))
    if not reason.is_failure:
        client.subscribe(PREFIX + '/#', qos=0)


def subscribe(_client, _userdata, _mid, reasons, _properties):
    log('MQTT_SUBACK', reasons=[str(value) for value in reasons])
    if reasons and all(not value.is_failure for value in reasons):
        ready.set()


def message(_client, _userdata, value):
    received_ns = time.perf_counter_ns()
    raw = value.payload.decode('utf-8', errors='replace')
    try:
        body = json.loads(raw)
    except ValueError:
        body = raw
    item = dict(topic=value.topic, retain=value.retain, qos=value.qos, body=body, received_ns=received_ns)
    messages.append(item)
    if value.topic.endswith('/ack') and isinstance(body, dict):
        acks[body.get('command_id')] = item
    log('MQTT_MESSAGE', **item)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='task010-evidence-' + uuid4().hex[:10],
                     clean_session=True, protocol=mqtt.MQTTv311)
client.on_connect = connect
client.on_subscribe = subscribe
client.on_message = message


def start_capture():
    client.connect('127.0.0.1', 1883, keepalive=20)
    client.loop_start()
    if not ready.wait(5):
        raise RuntimeError('MQTT subscription not ready')


def nodes():
    status, result = api('GET', '/api/nodes')
    if status != 200:
        raise RuntimeError('nodes unavailable')
    return next(item for item in result if item['node_id'] == 'node_01')


def export_experiment(identifier):
    status, detail = api('GET', f'/api/experiments/{identifier}')
    if status != 200 or detail['ended_at'] is None:
        raise RuntimeError('experiment must exist and be stopped before comparison')
    status, history = api('GET', f'/api/nodes/node_01/history?experiment_id={identifier}&limit=1000')
    assert status == 200 and history['total'] <= 1000, 'pagination required'
    status, stats = api('GET', f'/api/stats?experiment_id={identifier}&node_id=node_01')
    assert status == 200
    status, data = api('GET', f'/api/experiments/{identifier}/export.csv')
    assert status == 200 and isinstance(data, str)
    csvpath = ROOT / f'experiment-{identifier}-{args.tag}.csv'
    csvpath.open('x', encoding='utf-8', newline='').write(data)
    rows = list(csv.DictReader(io.StringIO(data)))
    selected = [row for row in rows if row['node_id'] == 'node_01']
    assert len(selected) == history['total'] == stats['nodes'][0]['sample_count'] > 0
    assert {(row['boot_id'], row['seq']) for row in selected} == {
        (item['telemetry']['boot_id'], item['telemetry']['seq']) for item in history['items']}
    for row, item in zip(selected, history['items']):
        assert row['continuity'] == item['continuity'] and row['quality'] == item['quality']
        for key in ['uptime_ms', 'mode', 'environment', 'brightness_target', 'brightness_applied']:
            assert row[key] == str(item['telemetry'][key])
        assert row['received_at'] == item['received_at']
    sums = {key:sum(float(row[key]) for row in selected) for key in
            ['total_energy_wh', 'auto_energy_wh', 'baseline_wh', 'valid_uptime_s', 'covered_wall_s']}
    for key, value in sums.items():
        assert math.isclose(value, stats[key], rel_tol=1e-9, abs_tol=1e-9), (key, value, stats[key])
    duration = (datetime.fromisoformat(detail['ended_at'])-datetime.fromisoformat(detail['started_at'])).total_seconds()
    assert math.isclose(stats['coverage_percent'], sums['covered_wall_s']/duration*100, abs_tol=1e-5)
    assert math.isclose(stats['missing_wall_s']+stats['covered_wall_s'], duration, abs_tol=1e-5)
    save(f'experiment-{identifier}-comparison-{args.tag}.json',
         dict(result='PASS', samples=len(selected), sums=sums, stats=stats, experiment=detail,
              clock_basis=dict(energy='node_uptime', coverage='receiver_utc'),
              limitation='API/CSV live comparison; dashboard rendering and independent energy derivation separate'))
    print('EXPERIMENT_CSV_STATS PASS', identifier, len(selected), sums, flush=True)


log('START', phase=args.phase, python=platform.python_version(), machine=platform.platform(), args=vars(args))
try:
    if args.phase == 'snapshot':
        for path in ['/api/health', '/api/nodes', '/api/alerts', '/api/experiments',
                     '/api/stats?node_id=node_01', '/api/nodes/node_01/history?limit=1000']:
            api('GET', path)
        db_snapshot(args.tag)
        for filename in ['firmware.bin', 'firmware.elf']:
            for folder in [FIRMWARE/'.pio/build/esp32dev', FIRMWARE/'simulations/node_01/build']:
                path = folder / filename
                log('ARTIFACT', path=str(path), size=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        response = httpx.get('http://127.0.0.1:5500/config.js', trust_env=False)
        log('DASHBOARD_CONFIG', status=response.status_code, body=response.text)
    elif args.phase == 'capture':
        start_capture()
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            for path in ['/api/health', '/api/nodes']:
                try:
                    api('GET', path)
                except httpx.HTTPError as error:
                    log('HTTP_UNAVAILABLE', path=path, error=str(error))
            time.sleep(1)
    elif args.phase == 'experiment-export':
        export_experiment(args.experiment_id)
    elif args.phase == 'reject':
        start_capture()
        current = nodes()['telemetry']
        for case in ['expired', 'wrong-boot', 'invalid-brightness']:
            identifier = str(uuid4())
            payload = dict(schema_version=1,node_id='node_01',boot_id=current['boot_id'],
                           command_id=identifier,deadline_uptime_ms=int(current['uptime_ms'])+5000,
                           mode='MANUAL',brightness=80)
            if case == 'expired':
                payload['deadline_uptime_ms'] = 0
            elif case == 'wrong-boot':
                payload['boot_id'] = ('0' if current['boot_id'][0] != '0' else '1')+current['boot_id'][1:]
            else:
                payload['brightness'] = 101
            log('REJECT_PROBE_SENT', case=case, body=payload, retain=False)
            client.publish(PREFIX+'/command',json.dumps(payload),qos=1,retain=False).wait_for_publish(timeout=3)
            deadline = time.monotonic()+12
            while identifier not in acks and time.monotonic()<deadline:
                time.sleep(.05)
            expected = {'expired':'EXPIRED','wrong-boot':'BOOT_MISMATCH','invalid-brightness':'INVALID_COMMAND'}[case]
            ack = acks.get(identifier)
            assert ack and ack['body']['result']=='REJECTED' and ack['body']['reason']==expected, (case, ack)
            log('REJECT_RESULT', case=case, result='PASS', ack=ack)
            print('REJECT PASS', case, identifier, flush=True)
    elif args.phase == 'cache':
        start_capture()
        summary = json.loads((ROOT/'command-latency-command-latency.json').read_text(encoding='utf-8'))
        original = summary['samples'][-1]['command']['payload']
        # HTTP exposes uint64 as decimal strings; MQTT v1 requires JSON integers.
        original['deadline_uptime_ms'] = int(original['deadline_uptime_ms'])
        assert original['mode']=='AUTO'
        identifier = original['command_id']
        current = nodes()['telemetry']
        assert current['boot_id']==original['boot_id']
        assert int(current['uptime_ms'])>int(original['deadline_uptime_ms'])
        for case in ['same-after-deadline','different-content','original-again']:
            payload = dict(original)
            if case=='different-content':
                payload.update(mode='MANUAL',brightness=80)
            acks.pop(identifier,None)
            log('CACHE_PROBE_SENT',case=case,body=payload,retain=False)
            client.publish(PREFIX+'/command',json.dumps(payload),qos=1,retain=False).wait_for_publish(timeout=3)
            deadline=time.monotonic()+12
            while identifier not in acks and time.monotonic()<deadline:
                time.sleep(.05)
            ack=acks.get(identifier)
            expected='REJECTED' if case=='different-content' else 'APPLIED'
            assert ack and ack['body']['result']==expected,(case,ack)
            if expected=='REJECTED':
                assert ack['body']['reason']=='INVALID_COMMAND'
            log('CACHE_PROBE_RESULT',case=case,result='PASS',ack=ack)
        status,final=api('GET','/api/commands/'+identifier)
        assert status==200 and final['result']=='APPLIED'
        assert nodes()['telemetry']['mode']=='AUTO'
        print('CACHE PASS',identifier,'after deadline, changed content rejected, original ACK retained',flush=True)
    elif args.phase == 'pending':
        start_capture()
        deadline = time.monotonic()+20
        while not nodes()['can_command']:
            if time.monotonic()>deadline:
                raise RuntimeError('Node did not become commandable')
            time.sleep(.1)
        status, command = api('POST','/api/nodes/node_01/commands',dict(mode='AUTO'))
        assert status == 202 and command['result']=='PENDING'
        status, guarded = api('POST','/api/nodes/node_01/commands',dict(mode='AUTO'))
        assert status == 409, (status, guarded)
        identifier = command['command_id']
        deadline = time.monotonic()+12
        while command['result']=='PENDING' and time.monotonic()<deadline:
            time.sleep(.1)
            _, command = api('GET','/api/commands/'+identifier)
        assert command['result']=='APPLIED' and identifier in acks
        log('PENDING_GUARD_RESULT',result='PASS',command_id=identifier,second_post_status=409,final=command)
        print('PENDING_GUARD PASS',identifier,flush=True)
    elif args.phase == 'run':
        start_capture()
        assert api('GET','/api/health')[1]['status']=='OK'
        for body in [dict(mode='AUTO',brightness=80),dict(mode='MANUAL'),dict(mode='MANUAL',brightness=101),
                     dict(mode='MANUAL',brightness=True),dict(mode='MANUAL',brightness=80.5)]:
            assert api('POST','/api/nodes/node_01/commands',body)[0] == 422
        assert api('POST','/api/nodes/node_02/commands',dict(mode='AUTO'))[0] == 409
        assert api('GET','/api/commands/'+str(uuid4()))[0] == 404
        previous = api('GET','/api/experiments')[1]
        if any(item['ended_at'] is None for item in previous['items']):
            raise RuntimeError('User experiment already open; not changing it')
        binpath = FIRMWARE/'simulations/node_01/build/firmware.bin'
        status, experiment = api('POST','/api/experiments',dict(name='TASK-010 live command latency',
            configuration=dict(source='live Wokwi node_01',firmware_sha256=hashlib.sha256(binpath.read_bytes()).hexdigest(),
                               voltage_v=12,rated_power_w=24,api_port=8001),
            notes='10 alternating MANUAL80/AUTO commands; latency is server sent_at to real ACK; not EX-series'))
        assert status==201
        identifier = experiment['id']
        save(f'owned-experiment-{args.tag}.json',experiment)
        print('EXPERIMENT_STARTED',identifier,flush=True)
        results=[]
        try:
            for index in range(10):
                deadline=time.monotonic()+20
                while not nodes()['can_command']:
                    if time.monotonic()>deadline:
                        raise RuntimeError('Node did not become commandable')
                    time.sleep(.25)
                body=dict(mode='MANUAL',brightness=80) if index%2==0 else dict(mode='AUTO')
                sent_ns=time.perf_counter_ns()
                status,command=api('POST','/api/nodes/node_01/commands',body)
                assert status==202,(status,command)
                command_id=command['command_id']
                deadline=time.monotonic()+12
                while command['result']=='PENDING' and time.monotonic()<deadline:
                    time.sleep(.1)
                    status,command=api('GET','/api/commands/'+command_id)
                    assert status==200
                ack=acks.get(command_id)
                elapsed = ((datetime.fromisoformat(command['ack_at'])-datetime.fromisoformat(command['sent_at'])).total_seconds()*1000
                           if command['ack_at'] else None)
                entry=dict(index=index+1,command_id=command_id,result=command['result'],mode=body['mode'],
                           server_sent_to_ack_ms=elapsed,
                           client_request_to_mqtt_ack_ms=(ack['received_ns']-sent_ns)/1e6 if ack else None,
                           mqtt_ack=ack,command=command)
                results.append(entry)
                log('LATENCY_SAMPLE',**entry)
                print('LATENCY',index+1,command_id,command['result'],elapsed,flush=True)
                assert command['result']=='APPLIED' and ack is not None, entry
                time.sleep(1)
            values=[entry['server_sent_to_ack_ms'] for entry in results]
            summary=dict(result='PASS',count=len(values),median_ms=statistics.median(values),max_ms=max(values),
                         samples=results,source='actual server sent_at and ack_at, corroborated by MQTT ACK',
                         sensor_to_dashboard='PENDING: requires timestamped sensor action and observed rendered DOM',
                         machine=platform.platform(),python=platform.python_version(),
                         conditions='single node, backend8001, dashboard5500, receiver UTC; Wokwi speed not measured')
            save(f'command-latency-{args.tag}.json',summary)
        finally:
            api('POST',f'/api/experiments/{identifier}/stop')
        export_experiment(identifier)
        db_snapshot(args.tag)
    log('END',phase=args.phase,result='PASS')
except Exception as error:
    log('END',phase=args.phase,result='FAIL',error=repr(error))
    raise
finally:
    if ready.is_set():
        client.disconnect()
        client.loop_stop()
    http.close()
    logfile.close()
