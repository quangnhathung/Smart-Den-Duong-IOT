"""Audit one actual proxy test, retained DB rows, late ACK and restoration. No writes to live DB."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))
def lines(name):return [json.loads(x) for x in (ROOT/name).read_text(encoding='utf-8').splitlines()]
def dt(value):return datetime.fromisoformat(value)
def iso(value):return datetime.fromtimestamp(value,timezone.utc).isoformat()

summaries=list(ROOT.glob('ack-delay-check-*-summary.json'))
assert len(summaries)==1,'Exactly one driver invocation required'
summary=load(summaries[0].name);assert summary['result']=='PASS'
identifier=summary['command_id']
driver=lines(summaries[0].name.replace('-summary.json','.jsonl'))
capture=lines('capture-whole-test.jsonl')
assert capture[-1]['event']=='END'
posts=[x for x in driver if x['event']=='HTTP' and x['method']=='POST']
assert len(posts)==1 and posts[0]['status']==202
commands=[x for x in capture if x['event']=='MQTT_MESSAGE' and x['topic'].endswith('/command')]
assert len(commands)==2 and all(x['body']['command_id']==identifier for x in commands)
assert commands[0]['body']==commands[1]['body'],'Retry must use identical ID, deadline and body'

baseline=load('sqlite-baseline.json')['tables']
after=load('sqlite-final.json')['tables']
retained={}
for table,prior in baseline.items():
    key='command_id' if table=='commands' else 'id'
    current={str(x[key]):x for x in after[table]}
    assert all(str(x[key]) in current for x in prior),table
    if table in ['telemetry','commands','ack_events','availability','experiments']:
        assert all(x==current[str(x[key])] for x in prior),table
    else:
        for old in prior:
            new=current[str(old[key])]
            assert all(old[k]==new[k] for k in ['id','node_id','kind','started_at'])
            if old['ended_at'] is not None:assert new['ended_at']==old['ended_at']
    retained[table]={'before':len(prior),'after':len(current),'missing_old_rows':0}
old_ids={x['command_id'] for x in baseline['commands']}
new=[x for x in after['commands'] if x['command_id'] not in old_ids]
assert len(new)==1 and new[0]['command_id']==identifier
command=new[0]
assert command['result']=='TIMEOUT' and command['reason']=='ACK_TIMEOUT' and command['attempts']==2
assert command['ack_at'] is None and command['retry_at'] is not None
assert not any(x['result']=='PENDING' for x in after['commands'])
late=[x for x in after['ack_events'] if x['command_id']==identifier]
assert len(late)==2 and all(x['disposition']=='LATE_OR_DUPLICATE' for x in late)
assert all(x['received_at']-command['sent_at']>=11.9 for x in late)
proxy=lines(Path(summary['proxy_log']).name)
selected=[x for x in proxy if x['event']=='TARGET_SELECTED']
assert len(selected)==1 and selected[0]['command_id']==identifier
held=[x for x in proxy if x['event']=='REAL_ACK_HELD']
released=[x for x in proxy if x['event']=='REAL_ACK_RELEASED']
forwarded=[x for x in proxy if x['event']=='REAL_COMMAND_FORWARDED']
assert len(held)==len(released)==len(forwarded)==2
assert sorted(x['sha256'] for x in held)==sorted(x['sha256'] for x in released)
assert all(x['command_id']==identifier for x in held+released+forwarded)

observations=[x for x in driver if x['event']=='HTTP' and x['method']=='GET' and x['path'].endswith(identifier)]
first_timeout=next(x for x in observations if x['body']['result']=='TIMEOUT')
last_pending=[x for x in observations if x['body']['result']=='PENDING'][-1]
stop=load('proxy-stop-action.json')
assert stop['proxy_stopped'] and stop['backend_health']['status']=='OK' and not stop['backend_proxy_clients']
dashboard=load('dashboard-http-restored.json')
assert dashboard['dashboard_http']==200 and dashboard['api_health']['status']=='OK'
assert dashboard['api_cors']=='http://127.0.0.1:5500'
final_snapshot=lines('snapshot-final.jsonl')
health=next(x['body'] for x in final_snapshot if x['event']=='HTTP' and x['path']=='/api/health')
views=next(x['body'] for x in final_snapshot if x['event']=='HTTP' and x['path']=='/api/nodes')
node=next(x for x in views if x['node_id']=='node_01')
assert health['status']=='OK' and health['dropped_events']==0
assert node['telemetry']['boot_id']=='3268eb79'
assert node['telemetry']['mode']=='AUTO' and node['telemetry']['brightness_target']==node['telemetry']['brightness_applied']==25
post_restore=[x for x in capture if x['event']=='MQTT_MESSAGE' and x['topic'].endswith('/command')
              and dt(x['at'])>dt(stop['at'])]
assert not post_restore
result={'result':'PASS','command_id':identifier,'one_http_post':True,'mqtt_command_sends':2,
        'expected_application_retry_count':1,'unexpected_command_ids':[],
        'server_sent_at':iso(command['sent_at']),'server_retry_at':iso(command['retry_at']),
        'retry_delay_s':command['retry_at']-command['sent_at'],
        'timeout_observed_utc':first_timeout['at'],
        'timeout_observed_elapsed_s':summary['observed_timeout_wall_s'],
        'timeout_bounds_from_api_utc':[last_pending['at'],first_timeout['at']],
        'timeout_note':'DB has no timeout_at column; report first observed TIMEOUT, not an invented exact transition timestamp.',
        'real_ack_at_proxy_utc':[x['at'] for x in held],
        'real_ack_release_utc':[x['at'] for x in released],
        'ack_db_received_utc':[iso(x['received_at']) for x in late],
        'late_ack_dispositions':[x['disposition'] for x in late],
        'final_command':command,'raw_ack_bytes_unchanged':True,'retained_rows':retained,
        'restoration':{'backend_mqtt':1883,'api':8001,'proxy1884_stopped':True,
                       'health':health,'latest_node_snapshot':node,
                       'observed_commands_after_proxy_stop':0,
                       'dashboard_user_confirmed':True,'dashboard_user_observed_time':'2026-11-16T19:44:21+07:00',
                       'dashboard_user_seq_range':[963,969]},
        'limitations':['No claim of a naturally lost ACK: this is labeled delay injection of real firmware ACK.',
                       'Dashboard rendering restoration is user-confirmed; no new screenshot in repository.',
                       'Broker outage/offline fallback and sensor-to-Dashboard latency remain separate pending criteria.']}
with (ROOT/'final-audit.json').open('x',encoding='utf-8') as output:json.dump(result,output,indent=2)
print('FINAL_AUDIT PASS',identifier,'one POST, one expected retry, two late ACK, zero extra/replay')
print('TIMES',result['server_sent_at'],result['timeout_observed_utc'],result['real_ack_release_utc'])
print('ROWS',retained)
