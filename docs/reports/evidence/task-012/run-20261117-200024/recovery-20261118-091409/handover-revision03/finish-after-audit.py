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
 audit=json.load(open(q/'analysis-final.json'));assert audit['status']=='PASS' and audit['accepted_runs']==15 and not audit['errors'] and not audit['missing']
 status['audit_sha256']=hashlib.sha256((q/'analysis-final.json').read_bytes()).hexdigest()
 report=Path(json.load(open(out/'report-build.json'))['target']);slides=Path(json.load(open(out/'slides-build.json'))['target'])
 status['report']=str(report);status['slides']=str(slides);status['resume_reason']='Continue after preserved video01 harness result-field error; reuse final audited data and latest document builds';save()
 run('validate-word-final',[office_py,Path('/home/quangnhathung/.codex/skills/docx/scripts/office/validate.py'),report])
 run('validate-slides-final',[office_py,Path('/home/quangnhathung/.codex/skills/pptx/scripts/office/validate.py'),slides])
 proof=json.load(open(q/'word-preview-final-v05/proof.json'));assert proof['source_unchanged'] and proof['sha256']==hashlib.sha256(report.read_bytes()).hexdigest() and proof['process_stopped']
 office_env={'LD_LIBRARY_PATH':str(office/'wps-root/usr/lib')+':/usr/lib/office6'}
 run('render-slides-final',[office_py,q/'render-office.py',slides,q/'slide-preview-final-v05'],office_env)
 run('record-demo-retry',['node',root/'scripts/record-experiment-demo.cjs',q/'runtime.json'],{'SMARTLIGHT_PLAYWRIGHT_MODULE':'/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright'},timeout=1500)
 run('video-decode-playback',['node',q/'qa-video.cjs'],timeout=600)
 run('cold-start',[python,q/'cold-rehearsal.py'],timeout=360)
 run('cleanup',[python,q/'cleanup-runtime.py'],timeout=300)
 status['status']='AWAITING_VISUAL_REVIEW';status['current_step']='Review final23 Word pages,12 slides and16 video scenes before video approval and backup';status['finished_at']=datetime.datetime.now().astimezone().isoformat(timespec='seconds');save();print(json.dumps(status),flush=True)
except Exception as exc:
 import traceback
 status['status']='STOPPED_ON_ERROR';status['error']=repr(exc);status['traceback']=traceback.format_exc();save();print(status['traceback'],flush=True);raise
