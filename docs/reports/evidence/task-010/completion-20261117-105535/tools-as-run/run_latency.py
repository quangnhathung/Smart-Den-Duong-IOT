from urllib.request import Request,urlopen
from pathlib import Path
import json,sys
s=json.loads(Path('/tmp/task010-completion/state.json').read_text());out=Path(s['evidence']);pilot=sys.argv[1]=='pilot';rows=[]
sequence=[('Home',500),('End',850)] if pilot else [('Home' if i%2==0 else 'End',pause) for i,pause in enumerate([250,600,950,1300,1650,350,700,1050,1400,1750])]
for key,pause in sequence:
 data=json.dumps({'pilot':pilot,'key':key,'delay_ms':pause}).encode()
 with urlopen(Request('http://127.0.0.1:18767/trial',data=data,headers={'Content-Type':'application/json'}),timeout=18) as response:row=json.load(response)
 rows.append(row);print(json.dumps({k:row[k] for k in ['id','status','latency_interval_ms','reasons']},ensure_ascii=False),flush=True)
 if pilot and row['reasons']:break
(out/('latency-pilot-results.json' if pilot else 'latency-acceptance-results.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
