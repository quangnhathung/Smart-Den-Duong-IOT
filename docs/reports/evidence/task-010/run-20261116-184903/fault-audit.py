"""Audit already recorded OPEN_LOAD telemetry/API. Does not send commands or alter DB."""
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
snapshot = json.loads((ROOT/'sqlite-initial.json').read_text(encoding='utf-8'))
rows = snapshot['tables']['telemetry']
alerts = [row for row in snapshot['tables']['alerts'] if row['kind']=='OPEN_LOAD']
assert alerts and all(row['ended_at'] is not None for row in alerts)
decoded = [(row,json.loads(row['payload'])) for row in rows]
last_alert = alerts[-1]
at_start = next((row,value) for row,value in decoded if row['received_at']==last_alert['started_at'])
at_end = next((row,value) for row,value in decoded if row['received_at']==last_alert['ended_at'])
assert at_start[1]['faults']==['OPEN_LOAD'] and at_start[1]['current_adc']==0
assert at_end[1]['faults']==[] and at_end[1]['current_adc']==4095
interval = [(row,value) for row,value in decoded if
            alerts[0]['started_at']-15 <= row['received_at'] <= last_alert['ended_at']+15]
assert interval
assert all(value['mode']=='AUTO' and value['environment']=='NIGHT' and value['motion']=='NONE'
           and value['brightness_target']==25 and value['brightness_applied']==25 for row,value in interval)
assert len({value['boot_id'] for row,value in interval})==1

def utc(seconds):
    return datetime.fromtimestamp(seconds,timezone.utc).isoformat().replace('+00:00','Z')

with httpx.Client(base_url='http://127.0.0.1:8001',trust_env=False,timeout=5) as client:
    # Use padded window edges, not a telemetry timestamp rounded from float to ISO microseconds.
    params={'from':utc(alerts[0]['started_at']-15), 'to':utc(last_alert['ended_at']+15)}
    collected={}
    for name,path,query in [
        ('history','/api/nodes/node_01/history',dict(params,limit=1000)),
        ('alerts','/api/alerts',{'node_id':'node_01'}),
        ('stats','/api/stats',dict(params,node_id='node_01')),
    ]:
        response=client.get(path,params=query)
        assert response.status_code==200
        collected[name]={'at':datetime.now(timezone.utc).isoformat(),'url':str(response.url),
                         'status':response.status_code,'body':response.json()}
    history=collected['history']['body']
    assert history['total']==len(interval)
    api_rows={int(item['id']):item for item in history['items']}
    for row,value in interval:
        assert api_rows[row['id']]['telemetry']['faults']==value['faults']
        assert int(api_rows[row['id']]['telemetry']['uptime_ms'])==value['uptime_ms']
    api_alerts={row['id']:row for row in collected['alerts']['body']['items']}
    for alert in alerts:
        assert api_alerts[alert['id']]['ended_at']==utc(alert['ended_at'])
    excluded=collected['stats']['body']['nodes'][0]['excluded_intervals']
    assert excluded.get('FAULT_OR_RECOVERY',0)>0
    assert excluded.get('LOAD_CALIBRATION_OR_FAULT_CONFIRMATION',0)>0

payload=dict(result='PASS',source='existing real SQLite telemetry plus live read API; no fault retest',
             boot_id=at_end[1]['boot_id'],alerts=alerts,
             last_fault_start_telemetry=at_start,last_recovery_telemetry=at_end,
             user_serial_recovery_uptime_ms=1340431,
             telemetry_recovery_uptime_ms=at_end[1]['uptime_ms'],
             serial_minus_telemetry_ms=1340431-at_end[1]['uptime_ms'],
             steady_auto25_samples=len(interval),interval=interval,api=collected,
             user_confirmed_fields={'ldr_lux':1,'pir':0,'duty':64,'mqtt':1,
                                    'serial_screenshot':'user reports captured; not present in repository'},
             limitations=['Raw MQTT recorder from preceding run ended before fault actions.',
                          'SQLite rows preserve telemetry payloads, not original MQTT packet arrival metadata.',
                          'Serial and telemetry sample/log moments are distinct; do not replace either timestamp.',
                          'Not an independent verification of exact 2s/3s detector boundaries from sparse samples.'])
with (ROOT/'fault-audit.json').open('x',encoding='utf-8') as stream:
    json.dump(payload,stream,indent=2)
print('OPEN_LOAD AUDIT PASS',len(interval),'samples; alerts',[row['id'] for row in alerts],
      'last recovery uptime',at_end[1]['uptime_ms'],'serial',1340431,'excluded',excluded)
