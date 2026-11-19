import datetime,json,os,re,signal,subprocess,time
from pathlib import Path
root=Path('/home/quangnhathung/HungQuang_WorkSpace/Learing/Iot/DoAn/firmware');out=root/'docs/reports/evidence/task-024'
def run(args):return subprocess.run(args,capture_output=True,text=True,timeout=20)
status=run(['code','--status']);assert status.returncode==0
(out/'code-status-before.txt').write_text(status.stdout)
proof={'at':datetime.datetime.now().astimezone().isoformat(),'actions':[]}
windows={}
for line in status.stdout.splitlines():
 m=re.search(r'\s(\d+)\s+window \[(\d+)\] \((.*)\)',line)
 if m and any(m[3].endswith(' - '+role+' - Visual Studio Code') for role in ['node_01','node_02','node_03','dashboard']):windows[m[2]]=int(m[1])
assert len(windows)==4,windows
pids=set(windows.values())
for line in status.stdout.splitlines():
 m=re.search(r'\s(\d+)\s+(?:extension-host|file-watcher) \[(\d+)\]',line)
 if m and m[2] in windows:pids.add(int(m[1]))
owned=[]
for pid in pids:
 p=Path('/proc')/str(pid)
 if p.exists():owned.append((pid,(p/'stat').read_text().split()[21]))
# Graceful backend stop; confirm ownership against startup proof.
s=json.loads((root/'output/task-023/startup.json').read_text())
assert s['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
for item in s['processes']:
 p=Path('/proc')/str(item['pid'])
 if p.exists():
  assert (p/'stat').read_text().split()[21]==item['start_ticks']
  args=(p/'cmdline').read_bytes().split(b'\0');assert b'uvicorn' in args and b'smartlight.api:app' in args
  os.kill(item['pid'],signal.SIGTERM);proof['actions'].append({'role':'backend','pid':item['pid']})
# These are only renderer/extension host/file watcher processes mapped to project windows.
for pid,ticks in owned:
 p=Path('/proc')/str(pid)
 try:
  if (p/'stat').read_text().split()[21]==ticks:
   os.kill(pid,signal.SIGTERM);proof['actions'].append({'role':'project-code-process','pid':pid,'start_ticks':ticks})
 except FileNotFoundError:pass
r=run(['docker','compose','-f',str(root/'infra/compose.yaml'),'stop','-t','5','mosquitto']);proof['broker_stop']={'exit':r.returncode,'stderr':r.stderr};assert r.returncode==0
ports=[1883,8000,5500,4000,4001,4002]
for _ in range(20):
 listeners=run(['ss','-ltnp']).stdout
 active=[line for line in listeners.splitlines() if any(':'+str(port)+' ' in line for port in ports)]
 if not active:break
 time.sleep(.5)
proof.update(verified_at=datetime.datetime.now().astimezone().isoformat(),remaining_project_listeners=active,listeners_after=listeners,status='STOPPED' if not active else 'NEEDS_FOLLOWUP')
(out/'stop-all.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
assert not active
