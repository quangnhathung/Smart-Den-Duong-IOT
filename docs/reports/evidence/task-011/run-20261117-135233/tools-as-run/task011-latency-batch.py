import sys,json,time,subprocess
from urllib.request import Request,urlopen
node='node_0'+sys.argv[1]
def call(path,body=None,port=18773):
    with urlopen(Request(f'http://127.0.0.1:{port}'+path,data=None if body is None else json.dumps(body).encode(),headers={'Content-Type':'application/json'}),timeout=20) as r:return json.loads(r.read())
subprocess.run(['python3','/tmp/task011-arrange.py',sys.argv[1]],check=True)
call('/go',{'node':node})
subprocess.run(['node','/tmp/task011-scroll.cjs'],check=True)
time.sleep(2)
ns=call('/api/nodes',port=8001);value=next(n for n in ns if n['node_id']==node)['telemetry']['ldr_adc']
pilotkey='Home' if value<100 else 'End'
row=call('/trial',{'node':node,'key':pilotkey,'pilot':True});print('PILOT',json.dumps(row),flush=True)
key='End' if pilotkey=='Home' else 'Home'
for i in range(10):
    subprocess.run(['node','/tmp/task011-scroll.cjs'],check=True,stdout=subprocess.DEVNULL)
    time.sleep(.75)
    row=call('/trial',{'node':node,'key':key});print(json.dumps(row),flush=True)
    # Keep all ten measurements, including failures; no cherry-picking or threshold changes.
    key='End' if key=='Home' else 'Home'
