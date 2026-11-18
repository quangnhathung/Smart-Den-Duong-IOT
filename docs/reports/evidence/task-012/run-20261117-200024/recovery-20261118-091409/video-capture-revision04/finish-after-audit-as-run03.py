"""Continue authorized local handover steps after all15 formal runs pass."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys,time
q=Path(__file__).resolve().parent;cfg=json.load(open(q/'runtime.json'));root=Path(cfg['root']);out=root/'output/task-012/deliverables';python=Path(root.parent/'backend/.venv/bin/python');office=q/'runtime/office';office_py=office/'venv/bin/python';stamp=datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S');steps=q/('handover-steps-'+stamp);steps.mkdir();status={'status':'WAITING_CAMPAIGN','started_at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'steps':[]}
def save(): (q/'pipeline-status.json').write_text(json.dumps(status,indent=2)+'\n')
def run(name,args,extra=None,timeout=1200):
 status['status']='RUNNING';status['current_step']=name;save();print(name,flush=True)
 target=steps/(name+'.log');env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',**(extra or {}));start=time.time()
 with target.open('w') as stream:process=subprocess.run([str(a) for a in args],cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
 item={'name':name,'returncode':process.returncode,'elapsed_s':time.time()-start,'log':str(target)};status['steps'].append(item);save()
 if process.returncode:raise RuntimeError('Step failed: '+name+'; inspect '+str(target))
 return target
try:
 audit=json.load(open(q/'analysis-final.json'));assert audit['status']=='PASS' and audit['accepted_runs']==15 and not audit['errors']
 status['audit_sha256']=hashlib.sha256((q/'analysis-final.json').read_bytes()).hexdigest()
 office_qa=json.load(open(root/'docs/reports/evidence/task-012/run-20261117-200024/office-final-qa.json'));assert office_qa['status']=='PASS'
 for item in office_qa['reviews'].values():assert hashlib.sha256(Path(item['source']).read_bytes()).hexdigest()==item['sha256']
 assert json.load(open(q/'cold-start.json'))['status']=='PASS'
 assert json.load(open(q/'video-runtime-startup.json'))['status']=='PASS'
 status['resume_reason']='Video02 visual QA failed on gray captured region; short headless scroll/download regression passed. Reuse unchanged audited data, validated/visually reviewed documents and successful cold-start.'
 status['reused_cold_start_sha256']=hashlib.sha256((q/'cold-start.json').read_bytes()).hexdigest();save()
 run('record-demo-headless',['node',root/'scripts/record-experiment-demo.cjs',q/'runtime.json'],{'SMARTLIGHT_PLAYWRIGHT_MODULE':'/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright'},timeout=1500)
 run('video-decode-playback',['node',q/'qa-video.cjs'],timeout=600)
 run('cleanup-final',[python,q/'cleanup-runtime.py'],timeout=300)
 status['status']='AWAITING_VISUAL_REVIEW';status['current_step']='Review final16 video scenes, approve video and create backup/closure docs';status['finished_at']=datetime.datetime.now().astimezone().isoformat(timespec='seconds');save();print(json.dumps(status),flush=True)
except Exception as exc:
 import traceback
 status['status']='STOPPED_ON_ERROR';status['error']=repr(exc);status['traceback']=traceback.format_exc();save();print(status['traceback'],flush=True);raise
