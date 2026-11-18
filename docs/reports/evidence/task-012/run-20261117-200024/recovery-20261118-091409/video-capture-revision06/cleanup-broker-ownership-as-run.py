"""Stop only current-boot owned QA resources after all handover captures."""
from pathlib import Path
import datetime,json,os,signal,socket,time
q=Path(__file__).resolve().parent;root=Path(json.load(open(q/'runtime.json'))['root']);boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();rows=json.load(open(q/'owned-processes.json'));result={'status':'INCOMPLETE','at':datetime.datetime.now().astimezone().isoformat(timespec='seconds'),'stopped':[],'errors':[]}
def state(item):
 proc=Path('/proc')/str(item['pid'])
 if not proc.exists():return None
 stat=(proc/'stat').read_text().split()
 return stat if stat[21]==item['proc_start_ticks'] and stat[2]!='Z' else None
try:
 assert not any(state(v) for v in rows if v.get('host_boot_id')==boot and v['name'] in ['ALL','pilot']),'Measurement still active'
 for name in ['ui','dashboard','collector','vscode-node_01','vscode-node_02','vscode-node_03','liveserver','backend','broker']:
  item=next(v for v in reversed(rows) if v['name']==name and (v.get('host_boot_id')==boot or (name=='broker' and 'host_boot_id' not in v)))
  if not state(item):continue
  if name=='broker' and 'host_boot_id' not in item:
   actual=(Path('/proc')/str(item['pid'])/'cmdline').read_bytes().rstrip(b'\0').decode().split('\0')
   assert actual==item['args'],'Broker argv differs from owned metadata'
   result['broker_ownership_observation']={'pid':item['pid'],'proc_start_ticks':item['proc_start_ticks'],'current_host_boot_id':boot,'exact_argv_verified':True,'note':'owned_broker start omitted host_boot_id; PID/ticks/exact argv and process group independently verified'}
  cmd=(Path('/proc')/str(item['pid'])/'cmdline').read_bytes().decode();assert str(q) in cmd or str(root/'scripts') in cmd or (name=='backend' and 'uvicorn' in cmd),name
  assert os.getpgid(item['pid'])==item['pid'],'Unexpected process group'
  os.killpg(item['pid'],signal.SIGTERM);end=time.monotonic()+20
  while state(item) and time.monotonic()<end:time.sleep(.1)
  if state(item):result['errors'].append('Owned process did not stop: '+name)
  else:result['stopped'].append(dict(name=name,pid=item['pid']))
 ports=[1883,8001,5500,4000,4001,4002,19222,19223,19224,18771,18772,18773]
 end=time.monotonic()+20
 while True:
  occupied=[]
  for port in ports:
   with socket.socket() as sock:
    if sock.connect_ex(('127.0.0.1',port))==0:occupied.append(port)
  if not occupied or time.monotonic()>end:break
  time.sleep(.25)
 result['ports_still_open']=occupied
 if occupied:result['errors'].append('QA ports remain open; unknown processes were not stopped')
 office=[]
 for name in ['word-preview-final-*','slide-preview-final-*']:
  for directory in q.glob(name):
   proof=json.load(open(directory/'proof.json'));pid=proof['owned_pid'];proc=Path('/proc')/str(pid);alive=proc.exists() and (proc/'stat').read_text().split()[21]==proof['start_ticks'] and (proc/'stat').read_text().split()[2]!='Z'
   office.append({'proof':str(directory/'proof.json'),'pid':pid,'stopped':not alive})
   if alive:result['errors'].append('Office QA instance remains; inspect ownership and document count before stopping')
 result['office']=office;result['status']='PASS' if not result['errors'] else 'INCOMPLETE'
except Exception as exc:
 import traceback
 result['errors'].append(repr(exc));result['traceback']=traceback.format_exc()
(q/'cleanup.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['status']=='PASS' else 1)
