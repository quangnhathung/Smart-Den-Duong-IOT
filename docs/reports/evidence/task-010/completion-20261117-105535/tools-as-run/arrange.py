import subprocess,json,os
from pathlib import Path
state=json.loads(Path('/tmp/task010-completion/state.json').read_text());out=Path(state['evidence'])
def x(*args):return subprocess.run(['xdotool',*map(str,args)],check=True,text=True,capture_output=True,timeout=5).stdout.strip()
def ancestors(pid):
 result=[]
 while pid>1:
  result.append(pid)
  try:pid=int(next(l for l in Path(f'/proc/{pid}/status').read_text().splitlines() if l.startswith('PPid:')).split()[1])
  except Exception:break
 return result
owned=[]
for name,pattern,parent,left in [('wokwi','Wokwi Simulator - wokwi-project',156833,0),('dashboard','SmartLight',164254,960)]:
 previous=json.loads((out/'video-windows.json').read_text()) if (out/'video-windows.json').exists() else []
 ids=[item['window_id'] for item in previous if item['name']==name] or x('search','--name',pattern).splitlines();matches=[]
 for wid in ids:
  pid=int(x('getwindowpid',wid));chain=ancestors(pid)
  if parent in chain:matches.append((wid,pid))
 if len(matches)!=1:raise RuntimeError(f'Expected one owned {name} window, got {matches}')
 wid,pid=matches[0];subprocess.run(['bspc','node',hex(int(wid)),'-g','hidden=off'],check=False,timeout=5);subprocess.run(['bspc','node',hex(int(wid)),'-d','focused'],check=True,timeout=5);subprocess.run(['bspc','node',hex(int(wid)),'-t','floating'],check=False,timeout=5);x('windowsize',wid,960,1040);x('windowmove',wid,left,0);x('windowraise',wid)
 owned.append({'name':name,'window_id':wid,'pid':pid,'owner_ancestor':parent,'title':x('getwindowname',wid),'geometry':x('getwindowgeometry','--shell',wid)})
(out/'video-windows.json').write_text(json.dumps(owned,ensure_ascii=False,indent=2)+'\n');print(json.dumps(owned,ensure_ascii=False))
