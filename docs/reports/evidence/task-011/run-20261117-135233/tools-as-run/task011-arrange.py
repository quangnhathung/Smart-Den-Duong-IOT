from pathlib import Path
import json,subprocess,sys
s=json.loads(Path('/tmp/task011-active.json').read_text());qa=Path(s['qa']);out=Path(s['evidence']);target=int(sys.argv[1]) if len(sys.argv)>1 else 0
browser=json.loads((out/'owned-dashboard-browser.json').read_text())['chrome_pid']
def x(*a):return subprocess.check_output(['xdotool',*map(str,a)],text=True,timeout=5).strip()
found=[]
for i in range(1,4):
    matches=[]
    for wid in x('search','--name',f'node_0{i}').splitlines():
        try:
            pid=int(x('getwindowpid',wid));cmd=Path(f'/proc/{pid}/cmdline').read_bytes().decode()
            if str(qa) in cmd:matches.append((wid,pid))
        except Exception:pass
    if len(matches)!=1:raise RuntimeError(f'Owned node {i} window matches: {matches}')
    wid,pid=matches[0];found.append({'node':i,'wid':wid,'pid':pid})
matches=[]
for wid in x('search','--pid',browser).splitlines():
    try:
        if 'SmartLight' in x('getwindowname',wid):matches.append(wid)
    except Exception:pass
assert len(matches)==1,matches
found.append({'node':4,'wid':matches[0],'pid':browser})
for item in found:
    n=item['node'];wid=item['wid'];subprocess.run(['bspc','node',hex(int(wid)),'-g','hidden=off'],capture_output=True);subprocess.run(['bspc','node',hex(int(wid)),'-d','focused'],capture_output=True);v=json.loads(subprocess.check_output(['bspc','query','-T','-n',hex(int(wid))],text=True));
    if v['client']['state']!='floating':subprocess.run(['bspc','node',hex(int(wid)),'-t','floating'],capture_output=True,check=True)
    width,height,left,top=(960,520,((n-1)%2)*960,((n-1)//2)*520)
    if target and n in (target,4):width,height,left,top=(960,1040,0 if n==target else 960,0)
    x('windowsize',wid,width,height);x('windowmove',wid,left,top)
    subprocess.run(['xprop','-id',wid,'-f','_NET_WM_WINDOW_OPACITY','32c','-set','_NET_WM_WINDOW_OPACITY','4294967295'],capture_output=True,check=True)
for item in found:
    v=json.loads(subprocess.check_output(['bspc','query','-T','-n',hex(int(item['wid']))],text=True));print(item['node'],v['client']['state'],v['client']['shown'])
for n in ([target,4] if target else [1,2,3,4]):x('windowraise',next(v['wid'] for v in found if v['node']==n))
(out/'owned-window-layout.json').write_text(json.dumps({'target':target,'windows':found},indent=2)+'\n');print('Arranged verified owned QA windows, target',target)
