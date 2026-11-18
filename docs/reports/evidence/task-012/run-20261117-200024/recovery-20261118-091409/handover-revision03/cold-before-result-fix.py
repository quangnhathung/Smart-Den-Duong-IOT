"""Owned QA cold start. Invoke only after15 valid runs and video recording."""
from pathlib import Path
import datetime,hashlib,json,os,signal,sqlite3,subprocess,sys,time,urllib.request
q=Path(__file__).resolve().parent;cfg=json.load(open(q/'runtime.json'));root=Path(cfg['root']);audit=json.load(open(q/'analysis-final.json'));assert audit['status']=='PASS' and audit['accepted_runs']==15
assert json.load(open(q/'demo-status.json'))['status'] in ['RECORDED','QA_PASSED']
result={'status':'INCOMPLETE','started_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'stopped':[]}
def save(): (q/'cold-start.json').write_text(json.dumps(result,indent=2)+'\n')
def req(port,route,body=None):
 data=json.dumps(body).encode() if body is not None else None
 with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+route,data=data,headers={'Content-Type':'application/json'}),timeout=8) as r:return json.load(r)
def live(item):
 p=Path('/proc')/str(item['pid'])
 if not p.exists():return False
 s=(p/'stat').read_text().split();return s[21]==item['proc_start_ticks'] and s[2]!='Z'
def hash_history(bound=None):
 c=sqlite3.connect(f"file:{cfg['database']}?mode=ro",uri=True);c.row_factory=sqlite3.Row
 bound=bound or c.execute('select max(id) from telemetry').fetchone()[0];h=hashlib.sha256();count=0
 for row in c.execute('select * from telemetry where id<=? order by id',(bound,)):
  h.update((json.dumps(dict(row),sort_keys=True,separators=(',',':'))+'\n').encode());count+=1
 pending=c.execute("select count(*) from commands where status='PENDING'").fetchone()[0];opened=c.execute('select count(*) from experiments where ended_at is null').fetchone()[0];check=[r[0] for r in c.execute('pragma quick_check')];c.close();return dict(max_id=bound,sha256=h.hexdigest(),count=count,pending=pending,open_experiments=opened,quick_check=check)
def wait_for(test,seconds=45):
 end=time.monotonic()+seconds;last=None
 while time.monotonic()<end:
  try:
   value=test()
   if value:return value
  except Exception as e:last=repr(e)
  time.sleep(.25)
 raise RuntimeError('Readiness timeout '+str(last))
def phase(name):
 p=subprocess.run([sys.executable,str(q/'resume-runtime.py'),name],capture_output=True,text=True,timeout=30);result.setdefault('startup',[]).append({'phase':name,'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode});save();assert p.returncode==0,p.stderr
try:
 result['desktop_before']=subprocess.check_output(['bspc','query','-D','-d','focused','--names'],text=True,timeout=5).strip()
 owners=json.load(open(q/'owned-processes.json'))
 assert not any(live(v) for v in owners if v['name'] in ['ALL','pilot']),'Campaign still active'
 result['history_before']=hash_history();assert result['history_before']['pending']==0 and result['history_before']['open_experiments']==0
 result['nodes_before']=req(8001,'/api/nodes');save()
 names=['ui','dashboard','collector','vscode-node_01','vscode-node_02','vscode-node_03','liveserver','backend','broker']
 for name in names:
  item=next(v for v in reversed(owners) if v['name']==name)
  if not live(item):continue
  cmd=(Path('/proc')/str(item['pid'])/'cmdline').read_bytes().decode();assert str(q) in cmd or str(root/'scripts') in cmd or (name=='backend' and 'uvicorn' in cmd),name
  assert os.getpgid(item['pid'])==item['pid'],'QA process group ownership differs'
  os.killpg(item['pid'],signal.SIGTERM)
  wait_for(lambda:not live(item),15);result['stopped'].append({'name':name,'pid':item['pid']});save()
 def ports_closed():
  import socket
  for port in [1883,8001,5500,4000,4001,4002,19222,19223,19224,18771,18772,18773]:
   with socket.socket() as sock:
    if sock.connect_ex(('127.0.0.1',port))==0:return False
  return True
 wait_for(ports_closed,20)
 result['all_services_stopped_at']=datetime.datetime.now().astimezone().isoformat(timespec='seconds');save()
 phase('core')
 for port in [19222,19223,19224]:wait_for(lambda:json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json',timeout=2)),45)
 phase('ui');wait_for(lambda:req(18772,'/state'),30)
 for node in [1,2,3]:req(18772,'/action',{'node':node,'kind':'start'})
 phase('collector');phase('dashboard')
 wait_for(lambda:req(18771,'/state').get('serial') and len(req(18771,'/state')['serial'])==3,30)
 nodes=wait_for(lambda:(lambda values:values if all(v['connection']=='ONLINE' and v['freshness']=='FRESH' for v in values) else None)(req(8001,'/api/nodes')),45)
 result['nodes_after']=nodes;result['health']=req(8001,'/api/health');assert result['health']['status']=='OK' and result['health']['dropped_events']==0
 old={v['node_id']:v['telemetry']['boot_id'] for v in result['nodes_before']}
 assert all(v['telemetry']['mode']=='AUTO' and v['telemetry']['boot_id']!=old[v['node_id']] for v in nodes)
 submitted=req(8001,'/api/nodes/node_01/commands',{'mode':'AUTO'});result['command_submitted']=submitted
 end=time.monotonic()+15
 while time.monotonic()<end:
  command=req(8001,'/api/commands/'+submitted['command_id'])
  if command['status']!='PENDING':break
  time.sleep(.2)
 assert command['status']=='APPLIED',command
 result['command_final']=command
 result['history_after']=hash_history(result['history_before']['max_id']);assert result['history_after']['sha256']==result['history_before']['sha256'] and result['history_after']['count']==result['history_before']['count'];assert result['history_after']['quick_check']==['ok']
 wait_for(lambda:req(18773,'/state'),30)
 isolated=subprocess.run([sys.executable,str(q/'resume-isolate.py')],capture_output=True,text=True,timeout=30)
 result['window_isolation']={'returncode':isolated.returncode,'stdout':isolated.stdout,'stderr':isolated.stderr};save();assert isolated.returncode==0
 subprocess.run(['bspc','desktop',result['desktop_before'],'-f'],check=True,timeout=5)
 result['desktop_after']=subprocess.check_output(['bspc','query','-D','-d','focused','--names'],text=True,timeout=5).strip();assert result['desktop_after']==result['desktop_before']
 req(18773,'/shot',{'name':'cold-start-dashboard.png'})
 result['status']='PASS';result['finished_at']=datetime.datetime.now().astimezone().isoformat(timespec='seconds');save();print(json.dumps({'status':result['status'],'history_preserved_rows':result['history_after']['count']}))
except Exception as e:
 import traceback
 result['error']=repr(e);result['traceback']=traceback.format_exc();save();raise
