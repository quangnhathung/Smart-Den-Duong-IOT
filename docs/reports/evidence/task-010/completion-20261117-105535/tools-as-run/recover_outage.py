from pathlib import Path
import json,time
from urllib.request import Request,urlopen
s=json.loads(Path('/tmp/task010-completion/state.json').read_text());out=Path(s['evidence']);p=out/'serial.jsonl';rows=[];deadline=time.monotonic()+15
while time.monotonic()<deadline:
 rows=[json.loads(x) for x in p.read_text().splitlines() if x.strip()]
 if any(x.get('fields',{}).get('mqtt')=='0' and x.get('fields',{}).get('environment')=='DAY' and x.get('fields',{}).get('applied')=='0' for x in rows[-25:]):break
 time.sleep(.2)
selected=[x for x in rows if x.get('fields',{}).get('mqtt')=='0' and x.get('fields',{}).get('mode')=='AUTO'];night=[x for x in selected if x['fields'].get('environment')=='NIGHT' and x['fields'].get('applied')=='25'];day=[x for x in selected if x['fields'].get('environment')=='DAY' and x['fields'].get('applied')=='0']
with urlopen(Request('http://127.0.0.1:18766/broker/start',data=b'{}',headers={'Content-Type':'application/json'}),timeout=15) as r:action=json.load(r)
result={'auto_offline_serial_pass':bool(night and day),'night_offline_sample':night[-1] if night else None,'day_offline_sample':day[0] if day else None,'restored_broker':action};(out/'offline-auto-serial-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));assert result['auto_offline_serial_pass']
