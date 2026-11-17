import json,re,statistics,hashlib
from pathlib import Path
S=json.loads(Path('/tmp/task011-active.json').read_text());OUT=Path(S['evidence']);source=OUT/'latency-trials.json';raw=source.read_bytes();all_rows=json.loads(raw);window=json.loads((OUT/'stability-02/start.json').read_text())
def lux(text):
    m=re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)(k?) lux',text.replace(',','').strip())
    if not m:raise ValueError('Unrecognized lux label '+repr(text))
    return float(m[1])*(1000 if m[2] else 1)
assert lux('0.1 lux')==.1 and lux('500 lux')==500 and lux('100k lux')==100000
rows=[];pilots=[]
for r in all_rows:
    if r.get('runtime')!='sensor-coalescing-fixed-cpu4':continue
    node=r['node'];action=r.get('action')
    if not action:continue
    low=action['browser_ms']+min(r['sensorClock']['offsetLow'],r['sensorAfter']['offsetLow']);high=action['browser_ms']+max(r['sensorClock']['offsetHigh'],r['sensorAfter']['offsetHigh'])
    if low<window['start_wall_ms']:continue
    errors=[];target=.1 if r['key']=='Home' else 100000
    before=lux(r['slider_before']);after=lux(r['slider_after'])
    if before==target or after!=target:errors.append('Slider did not change from opposite input to requested bound')
    for reason in r['reasons']:
        if reason!='Slider did not reach requested value':errors.append(reason)
    if not action['trusted'] or action['visibility']!='visible':errors.append('Action not trusted/visible')
    render=r.get('render');api=r.get('api',{}).get('node')
    if not render or not api:errors.append('Missing real API/render')
    else:
        t=api['telemetry'];baseline=r['baseline']['telemetry'];key=render['readings']['Boot / sequence']
        if api['node_id']!=node or render['node']!=node:errors.append('Node mismatch')
        if t['boot_id']!=window['boots'][node] or t['boot_id']!=baseline['boot_id']:errors.append('Boot mismatch')
        if int(t['seq'])<=int(baseline['seq']) or key!=t['boot_id']+' / '+t['seq']:errors.append('Sequence mismatch')
        adc=int(re.sub(r'[^0-9]','',render['readings']['LDR · ADC raw']))
        if adc!=t['ldr_adc'] or (r['key']=='Home' and adc<=3900) or (r['key']=='End' and adc>=100):errors.append('ADC target/render mismatch')
        if render['visibility']!='visible' or not render['ldr_visible']:errors.append('Rendering not visible')
    bounds=r['latency_interval_ms']
    status='INCOMPLETE' if errors or not bounds else 'PASS' if 0<=bounds[0]<=bounds[1]<=3000 else 'FAIL' if bounds[0]>3000 else 'INCOMPLETE'
    value={'id':r['id'],'node':node,'pilot':r['pilot'],'original_status':r['status'],'original_reasons':r['reasons'],'audited_status':status,'errors':errors,'bounds_ms':bounds,'slider_before_lux':before,'slider_after_lux':after,'key':r['key'],'action_host_bounds_ms':[low,high],'boot_id':r['baseline']['telemetry']['boot_id']}
    (pilots if r['pilot'] else rows).append(value)
summary={}
for node in ('node_01','node_02','node_03'):
    a=[r for r in rows if r['node']==node];good=[r for r in a if r['audited_status']=='PASS'];summary[node]={'samples':len(a),'pass':len(good),'fail':sum(r['audited_status']=='FAIL' for r in a),'incomplete':sum(r['audited_status']=='INCOMPLETE' for r in a),'status':'PASS' if len(a)==10 and len(good)==10 else 'PENDING'}
    if a:summary[node].update(median_interval_ms=[statistics.median(r['bounds_ms'][i] for r in a) for i in (0,1)],max_interval_ms=[max(r['bounds_ms'][i] for r in a) for i in (0,1)])
result={'status':'PASS' if all(s['status']=='PASS' for s in summary.values()) else 'PENDING','source':source.name,'source_sha256':hashlib.sha256(raw).hexdigest(),'window':'stability-02','method':'Independent audit of unchanged raw trials. Interpret Wokwi 100k lux as 100000 lux, exactly as observed aria-valuemax=100000 and End key. Correct only the known label-parser validation error; do not change timing or suppress valid latency failures.','scope':'Exactly ten main trials per node on final firmware, after acceptance window start; predefined pilots excluded, older firmware trials retained in source.','by_node':summary,'trials':rows,'pilots':pilots}
(OUT/'latency-final-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'by_node':summary},ensure_ascii=False))
