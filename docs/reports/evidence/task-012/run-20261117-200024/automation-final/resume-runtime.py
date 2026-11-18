from pathlib import Path
import datetime,hashlib,json,os,socket,subprocess,sys,time
q=Path(__file__).resolve().parent;cfg=json.load(open(q/'runtime.json'));root=Path(cfg['root']);phase=sys.argv[1];owners=q/'owned-processes.json'
def start(name,args,log,cwd=None,extra=None):
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',**(extra or {}));p=subprocess.Popen(args,cwd=cwd or root,env=env,stdout=(q/log).open('a'),stderr=subprocess.STDOUT,start_new_session=True)
 rows=json.load(open(owners));rows.append(dict(name=name,pid=p.pid,args=args,proc_start_ticks=Path(f'/proc/{p.pid}/stat').read_text().split()[21],host_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),started_at=datetime.datetime.now().astimezone().isoformat(timespec='seconds')));owners.write_text(json.dumps(rows,indent=2)+'\n');print(name,p.pid,flush=True)
if phase=='core':
 for port in [1883,8001,5500,4000,4001,4002,19222,19223,19224,18771,18772,18773]:
  with socket.socket() as sock:
   assert sock.connect_ex(('127.0.0.1',port))!=0,f'Port already in use:{port}'
 base=json.load(open(root/'docs/reports/evidence/task-012/run-20261117-200024/baseline.json'));changes=[]
 for name,info in base.items():
  repo=root if name=='firmware' else root.parent/name
  for rel,digest in info['hashes'].items():
   if name=='firmware' and not (rel.startswith(('src/','include/','simulations/')) or rel=='platformio.ini'):continue
   file=repo/rel
   if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:changes.append(name+'/'+rel)
 assert not changes,changes
 start('broker',[cfg['broker_binary'],'-c',cfg['broker_config'],'-v'],'broker.log',extra={'LD_LIBRARY_PATH':cfg['broker_library_dir']})
 start('backend',[str(root.parent/'backend/.venv/bin/python'),'-B','-m','uvicorn','smartlight.api:app','--host','127.0.0.1','--port','8001','--workers','1'],'backend.log',cwd=root.parent/'backend',extra={'SMARTLIGHT_DB':cfg['database']})
 start('liveserver',['node',str(q/'live.cjs')],'liveserver.log')
 for node,port in [('node_01',19222),('node_02',19223),('node_03',19224)]:
  start('vscode-'+node,['/usr/share/code/code','--new-window','--user-data-dir='+str(q/(node+'-profile')),'--extensions-dir='+str(q/'extensions'),'--remote-debugging-port='+str(port),'--skip-welcome','--skip-release-notes','--folder-uri='+str((q/node).as_uri()),'--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows'],'vscode-'+node+'.log')
elif phase=='restart-ui':
 import signal
 entry=next(v for v in reversed(json.load(open(owners))) if v['name']=='ui');proc=Path('/proc')/str(entry['pid'])
 assert proc.exists() and (proc/'stat').read_text().split()[21]==entry['proc_start_ticks']
 assert str(root/'scripts/experiment-ui.cjs') in (proc/'cmdline').read_bytes().decode()
 os.kill(entry['pid'],signal.SIGTERM)
 for _ in range(100):
  if not proc.exists() or (proc/'stat').read_text().split()[2]=='Z':break
  time.sleep(.05)
 start('ui',['node',str(root/'scripts/experiment-ui.cjs'),str(q/'runtime.json')],'ui.log',extra={'SMARTLIGHT_PLAYWRIGHT_MODULE':'/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright'})
elif phase=='ui':start('ui',['node',str(root/'scripts/experiment-ui.cjs'),str(q/'runtime.json')],'ui.log',extra={'SMARTLIGHT_PLAYWRIGHT_MODULE':'/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright'})
elif phase=='collector':start('collector',[str(root.parent/'backend/.venv/bin/python'),'-B',str(root/'scripts/experiment-collector.py'),str(q/'runtime.json')],'collector.log')
elif phase=='dashboard':start('dashboard',['node',str(root/'scripts/experiment-dashboard.cjs'),str(q/'runtime.json')],'dashboard.log',extra={'SMARTLIGHT_PLAYWRIGHT_MODULE':'/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright'})
elif phase=='video':
 start('video-runtime',[sys.executable,'-B',str(q/'start-video-runtime.py')],'video-runtime.log')
elif phase in ['finish','finish-audited']:
 for item in json.load(open(owners)):
  proc=Path('/proc')/str(item['pid'])
  if item['name']=='handover-pipeline' and proc.exists():
   stat=(proc/'stat').read_text().split();assert stat[21]!=item['proc_start_ticks'] or stat[2]=='Z','Handover pipeline already running'
 start('handover-pipeline',[sys.executable,'-B',str(q/('finish-after-audit.py' if phase=='finish-audited' else 'finish-pipeline.py'))],'finish-pipeline.log')
elif phase=='main':
 for item in json.load(open(owners)):
  proc=Path('/proc')/str(item['pid'])
  if item['name']=='ALL' and proc.exists():
   stat=(proc/'stat').read_text().split()
   assert stat[21]!=item['proc_start_ticks'] or stat[2]=='Z','An owned campaign is already running'
 for port in [18771,18772,18773]:
  with socket.socket() as sock:assert sock.connect_ex(('127.0.0.1',port))==0,f'QA service not ready:{port}'
 start('ALL',[str(root.parent/'backend/.venv/bin/python'),'-B',str(root/'scripts/experiments.py'),'run','--run-dir',str(q),'--all','--resume'],'main.log')
else:raise ValueError(phase)
