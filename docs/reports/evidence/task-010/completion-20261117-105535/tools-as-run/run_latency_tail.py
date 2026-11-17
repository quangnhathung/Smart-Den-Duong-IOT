from pathlib import Path
from urllib.request import Request,urlopen
import json
s=json.loads(Path('/tmp/task010-completion/state.json').read_text());out=Path(s['evidence']);rows=json.loads((out/'latency-trials.json').read_text());count=len([r for r in rows if not r['pilot']]);print('Resume after completed acceptance samples:',count,flush=True)
pauses=[250,600,950,1300,1650,350,700,1050,1400,1750]
for i in range(count,10):
 data=json.dumps({'pilot':False,'key':'Home' if i%2==0 else 'End','delay_ms':pauses[i]}).encode()
 with urlopen(Request('http://127.0.0.1:18767/trial',data=data,headers={'Content-Type':'application/json'}),timeout=18) as r:row=json.load(r)
 print(json.dumps({k:row[k] for k in ['id','status','latency_interval_ms','reasons']},ensure_ascii=False),flush=True)
rows=[r for r in json.loads((out/'latency-trials.json').read_text()) if not r['pilot']];(out/'latency-acceptance-results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
