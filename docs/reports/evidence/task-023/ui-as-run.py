import json,subprocess,sys,time
from pathlib import Path
root=Path('/home/quangnhathung/HungQuang_WorkSpace/Learing/Iot/DoAn/firmware');out=root/'output/task-023'
def x(*args):return subprocess.check_output(['xdotool',*map(str,args)],text=True,timeout=10).strip()
role=sys.argv[1];action=sys.argv[2] if len(sys.argv)>2 else 'inspect'
windows=[]
for w in x('search','--class','code').splitlines():
 name=x('getwindowname',w)
 if f' - {role} - Visual Studio Code' in name:windows.append((w,name))
assert len(windows)==1,windows
w,title=windows[0]
# Activate only the explicitly matched project window.
subprocess.run(['bspc','node',hex(int(w)),'-g','hidden=off'],capture_output=True)
x('windowactivate','--sync',w);time.sleep(.4)
if action=='start':
 command='Wokwi: Start Simulator' if role.startswith('node_') else 'Live Server: Open with Live Server'
 x('key','--clearmodifiers','ctrl+shift+p');time.sleep(.4);x('type','--clearmodifiers','--delay','30',command);time.sleep(.9);x('key','Return');time.sleep(5)
elif action=='key':x('key','--clearmodifiers',sys.argv[3]);time.sleep(1)
print(json.dumps({'window':w,'title':x('getwindowname',w),'action':action},ensure_ascii=False))
