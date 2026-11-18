from pathlib import Path
import json,subprocess,datetime
q=Path(__file__).resolve().parent;cfg=json.load(open(q/'runtime.json'));desktop='TASK012-QA'
def call(*args):return subprocess.check_output(args,text=True,timeout=5).strip()
focused=call('bspc','query','-D','-d','focused','--names')
if desktop not in call('bspc','query','-D','--names').splitlines():subprocess.run(['bspc','monitor','focused','-a',desktop],check=True)
owned=[]
for n in [1,2,3]:
 for wid in call('xdotool','search','--name',f'node_0{n}').splitlines():
  try:
   pid=int(call('xdotool','getwindowpid',wid));cmd=Path(f'/proc/{pid}/cmdline').read_bytes().decode()
   if str(q) not in cmd:continue
   subprocess.run(['bspc','node',hex(int(wid)),'-t','floating'],check=False)
   subprocess.run(['xdotool','windowsize',wid,'960','1000'],check=True)
   subprocess.run(['xdotool','windowmove',wid,str(0 if n==1 else 960),'30'],check=True)
   subprocess.run(['bspc','node',hex(int(wid)),'-d',desktop],check=True);owned.append(dict(wid=wid,pid=pid,node=n))
  except FileNotFoundError:pass
assert len(owned)==3,owned
browser=json.load(open(q/'owned-dashboard.json'));pid=browser['chrome_pid'];stat=Path(f'/proc/{pid}/stat').read_text().split();assert int(stat[3])==browser['controller_pid']
for wid in call('xdotool','search','--pid',str(pid)).splitlines():
 if 'SmartLight' in call('xdotool','getwindowname',wid):
  subprocess.run(['bspc','node',hex(int(wid)),'-d',desktop],check=True);owned.append(dict(wid=wid,pid=pid,app='dashboard'))
assert call('bspc','query','-D','-d','focused','--names')==focused,'User desktop focus changed'
stamp=datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S');(q/('isolation-'+stamp+'.json')).write_text(json.dumps(dict(desktop=desktop,user_desktop=focused,owned=owned),indent=2)+'\n');print('Isolated QA windows; user focus preserved',focused)
