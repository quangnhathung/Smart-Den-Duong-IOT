from pathlib import Path
import datetime,json,subprocess,sys,time,urllib.request
q=Path(__file__).resolve().parent;cfg=json.load(open(q/'runtime.json'));proof={'status':'INCOMPLETE','started_at':datetime.datetime.now().astimezone().isoformat()};target=q/'video-runtime-startup.json'
def save():target.write_text(json.dumps(proof,indent=2)+'\n')
def req(port,path,body=None):
 data=json.dumps(body).encode() if body is not None else None
 with urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{port}'+path,data=data,headers={'Content-Type':'application/json'}),timeout=5) as r:return json.load(r)
def wait(test,seconds=45):
 end=time.monotonic()+seconds;last=None
 while time.monotonic()<end:
  try:
   value=test()
   if value:return value
  except Exception as e:last=repr(e)
  time.sleep(.25)
 raise RuntimeError('Readiness timeout '+str(last))
def phase(name):
 p=subprocess.run([sys.executable,str(q/'resume-runtime.py'),name],capture_output=True,text=True,timeout=30);proof.setdefault('phases',[]).append({'name':name,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});save();assert not p.returncode,p.stderr
try:
 assert json.load(open(q/'analysis-final.json'))['accepted_runs']==15
 proof['desktop_before']=subprocess.check_output(['bspc','query','-D','-d','focused','--names'],text=True).strip();save()
 phase('core')
 for port in [19222,19223,19224]:wait(lambda:json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json',timeout=2)))
 phase('ui');wait(lambda:req(18772,'/state'))
 for n in [1,2,3]:req(18772,'/action',{'node':n,'kind':'start'})
 phase('collector');phase('dashboard')
 proof['nodes']=wait(lambda:(lambda values:values if len(values)==3 and all(v['connection']=='ONLINE' and v['freshness']=='FRESH' for v in values) else None)(req(8001,'/api/nodes')))
 wait(lambda:req(18773,'/state'));subprocess.run([sys.executable,str(q/'resume-isolate.py')],check=True,timeout=30)
 subprocess.run(['bspc','desktop',proof['desktop_before'],'-f'],check=True)
 proof['health']=req(8001,'/api/health');assert proof['health']['status']=='OK' and proof['health']['dropped_events']==0
 proof['status']='PASS';proof['finished_at']=datetime.datetime.now().astimezone().isoformat();save();print('Video QA runtime ready',flush=True)
except Exception as e:proof['error']=repr(e);save();raise
