from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import datetime,hashlib,json,sys,time
q=Path(__file__).resolve().parent;root=Path(json.load(open(q/'runtime.json'))['root']);sys.path.insert(0,str(root/'scripts'))
from experiment_tools.live import observer,perform,ui,request
from experiment_tools.recipes import Action,NODES
cfg=json.load(open(q/'runtime.json'));target=q/('scene-rehearsal-'+datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')+'.json');result={'status':'INCOMPLETE','purpose':'QA scene latency rehearsal outside formal experiment windows; never a formal accepted run','rounds':[],'ui_sha256':hashlib.sha256((root/'scripts/experiment-ui.cjs').read_bytes()).hexdigest()}
def save():target.write_text(json.dumps(result,indent=2)+'\n')
save()
try:
 assert all(v['ended_at'] for v in request(cfg['api'],'/api/experiments?limit=100&offset=0')['items']),'Formal experiment still open'
 deadline=time.monotonic()+20
 while True:
  try:
   request(cfg['ui'],'/state',timeout=3);break
  except Exception:
   if time.monotonic()>=deadline:raise
   time.sleep(.25)
 with ThreadPoolExecutor(max_workers=3) as pool:
  list(pool.map(lambda n:ui(cfg,n,'reset-cache'),NODES))
  list(pool.map(lambda n:ui(cfg,n,'scene',lux=100,distance=150,current=1023),NODES))
  for index in range(6):
   value={'environment':'NIGHT' if index%2==0 else 'TWILIGHT','distance':50 if index%2==0 else 150}
   list(pool.map(lambda n:ui(cfg,n,'prepare-scene',lux=.1 if index%2==0 else 100,distance=value['distance']),NODES));time.sleep(2)
   rows=list(pool.map(lambda n:perform(cfg,Action(0,n,'scene',value)),NODES))
   for row in rows:
    row['conservative_duration_node_ms']=row['physical_confirmation']['uptime_ms']-row['before_clock']['uptime_ms']
   result['rounds'].append({'index':index+1,'scene':value,'actions':rows});save();print(index+1,[r['conservative_duration_node_ms'] for r in rows],flush=True)
   time.sleep(2)
 result['maximum_conservative_node_ms']=max(r['conservative_duration_node_ms'] for v in result['rounds'] for r in v['actions'])
 result['status']='PASS' if result['maximum_conservative_node_ms']<=2000 else 'INCOMPLETE';save();print(json.dumps({'status':result['status'],'maximum_conservative_node_ms':result['maximum_conservative_node_ms'],'proof':str(target)}))
 if result['status']!='PASS':raise RuntimeError('Scene preparation still exceeds conservative2s bound')
except Exception as error:
 result['error']=repr(error);save();raise
