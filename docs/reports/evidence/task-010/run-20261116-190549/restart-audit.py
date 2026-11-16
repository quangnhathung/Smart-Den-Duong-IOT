"""Compare real pre/post-restart SQLite snapshots and read API, without modifying DB."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT=Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/'run-20261116-184903'
OLDER=ROOT.parent/'run-20261116-180648'
before=json.loads((PREVIOUS/'sqlite-final.json').read_text(encoding='utf-8'))
after=json.loads((ROOT/'sqlite-after-restart.json').read_text(encoding='utf-8'))
assert after['integrity']==['ok'] and after['schema_version']==before['schema_version']==1
assert after['db']==before['db']
retained={}
for table,old_rows in before['tables'].items():
    key='command_id' if table=='commands' else 'id'
    current={str(row[key]):row for row in after['tables'][table]}
    assert all(str(row[key]) in current for row in old_rows),table
    if table in ['telemetry','commands','ack_events','availability']:
        assert all(row==current[str(row[key])] for row in old_rows),table
    elif table=='alerts':
        for row in old_rows:
            new=current[str(row[key])]
            assert all(row[k]==new[k] for k in ['id','node_id','kind','started_at'])
            if row['ended_at'] is not None:
                assert row['ended_at']==new['ended_at']
    retained[table]={'before':len(old_rows),'after':len(current),'old_rows_missing':0}

rows=after['tables']['telemetry']
old_run=before['tables']['telemetry'][-1]['continuity'].split('/')[0]
new_run=rows[-1]['continuity'].split('/')[0]
assert old_run!=new_run
boundaries=[]
for left,right in zip(rows,rows[1:]):
    if left['continuity'].split('/')[0]!=right['continuity'].split('/')[0]:
        boundaries.append((left,right))
assert boundaries
left,right=boundaries[-1]
assert left['boot_id']==right['boot_id']=='3268eb79'
assert int(right['seq'])>int(left['seq'])
assert int(right['uptime_ms'])>int(left['uptime_ms'])
assert json.loads(right['payload'])['mode']=='AUTO'
assert json.loads(right['payload'])['brightness_applied']==25

def utc(value):
    return datetime.fromtimestamp(value,timezone.utc).isoformat().replace('+00:00','Z')

api={}
def get(client,name,path,params=None):
    response=client.get(path,params=params)
    assert response.status_code==200,(path,response.status_code,response.text)
    value=response.json() if 'json' in response.headers.get('content-type','') else response.text
    api[name]={'at':datetime.now(timezone.utc).isoformat(),'url':str(response.url),
               'status':response.status_code,'body':value}
    return value,response

with httpx.Client(base_url='http://127.0.0.1:8001',trust_env=False,timeout=5) as client:
    health,_=get(client,'health','/api/health')
    assert health['status']=='OK' and health['dropped_events']==0
    alerts,_=get(client,'alerts','/api/alerts',{'node_id':'node_01','limit':1000})
    openload={r['id']:r for r in alerts['items'] if r['kind']=='OPEN_LOAD'}
    assert all(openload[i]['ended_at'] is not None for i in [30,33])
    _,_=get(client,'experiments','/api/experiments')
    exports=[]
    for identifier,folder,tag in [(1,OLDER,'command-latency'),(2,OLDER,'passive-session'),(3,PREVIOUS,'night-observation')]:
        prior=json.loads((folder/f'experiment-{identifier}-comparison-{tag}.json').read_text())['experiment']
        detail,_=get(client,f'experiment-{identifier}',f'/api/experiments/{identifier}')
        assert detail==prior,identifier
        _,response=get(client,f'csv-{identifier}',f'/api/experiments/{identifier}/export.csv')
        original=(folder/f'experiment-{identifier}-{tag}.csv').read_bytes()
        assert response.content==original,identifier
        filename=f'experiment-{identifier}-after-restart.csv'
        (ROOT/filename).open('xb').write(response.content)
        exports.append({'id':identifier,'bytes':len(original),'sha256':hashlib.sha256(original).hexdigest(),
                        'same_bytes_as_pre_restart':True})
    params={'from':utc(left['received_at']-1),'to':utc(right['received_at']+1)}
    history,_=get(client,'restart-gap-history','/api/nodes/node_01/history',dict(params,limit=1000))
    assert {left['id'],right['id']} <= {row['id'] for row in history['items']}
    stats,_=get(client,'restart-gap-stats','/api/stats',dict(params,node_id='node_01'))
    assert stats['nodes'][0]['excluded_intervals'].get('DISCONTINUITY',0)>0
    assert stats['total_energy_wh']==0 and stats['valid_uptime_s']==0
    # The narrow padded window contains only the two actual boundary endpoints.
    assert history['total']==2,history['total']

result={'result':'PASS','scope':'History/closed experiments/alerts persistence and server-side restart gap',
        'before_snapshot':str(PREVIOUS/'sqlite-final.json'),'after_snapshot':str(ROOT/'sqlite-after-restart.json'),
        'database':after['db'],'retained_rows':retained,'old_backend_run_id':old_run,'new_backend_run_id':new_run,
        'boundary_before':left,'boundary_after':right,'boundary_received_at_utc':[utc(left['received_at']),utc(right['received_at'])],
        'same_firmware_boot':True,'csv_exports':exports,'api':api,
        'user_confirmation':{'old_pid':18828,'new_pid':43632,'workers':1,'init_db_rerun':False,
                             'sqlite_deleted_or_replaced':False,'wokwi_and_mosquitto_kept_running':True},
        'limitations':['Recorder started after restart; actual API outage and first stale startup state not captured.',
                       'No pending command or open measurement experiment existed at restart; those cases not claimed.',
                       'Server gap and unchanged CSV verified; actual Dashboard rendering after reload not captured here.']}
with (ROOT/'restart-audit.json').open('x',encoding='utf-8') as stream:
    json.dump(result,stream,indent=2)
print('RESTART_AUDIT PASS',retained,'run',old_run,'->',new_run,
      'boundary',left['id'],right['id'],'same boot',right['boot_id'],'CSV unchanged',len(exports))
