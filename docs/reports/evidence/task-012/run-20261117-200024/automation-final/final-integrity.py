"""Read-only integrity check after the owned QA services have stopped."""
from pathlib import Path
import datetime,hashlib,json,sqlite3
q=Path(__file__).resolve().parent;cfg=json.loads((q/'runtime.json').read_text());root=Path(cfg['root']);e=root/'docs/reports/evidence/task-012/run-20261117-200024'
assert json.loads((q/'cleanup.json').read_text())['status']=='PASS'
audit=json.loads((q/'analysis-final.json').read_text());assert audit['status']=='PASS' and audit['accepted_runs']==15
cold=json.loads((q/'cold-start.json').read_text());bound=cold['history_before']['max_id'];db=sqlite3.connect(f"file:{cfg['database']}?mode=ro",uri=True);db.row_factory=sqlite3.Row;h=hashlib.sha256();count=0
for row in db.execute('select * from telemetry where id<=? order by id',(bound,)):
 h.update((json.dumps(dict(row),sort_keys=True,separators=(',',':'))+'\n').encode());count+=1
check=[r[0] for r in db.execute('pragma quick_check')];pending=db.execute("select count(*) from commands where result='PENDING'").fetchone()[0];opened=db.execute('select count(*) from experiments where ended_at is null').fetchone()[0];counts={t:db.execute(f'select count(*) from {t}').fetchone()[0] for t in ['telemetry','commands','alerts','experiments','ingest_errors']};db.close()
assert count==cold['history_before']['count'] and h.hexdigest()==cold['history_before']['sha256']
assert check==['ok'] and pending==0 and opened==0
size=audit['raw_snapshot_bytes'];raw=hashlib.sha256()
with (q/'mqtt-events.jsonl').open('rb') as f:
 remaining=size
 while remaining:
  b=f.read(min(1024*1024,remaining));assert b;raw.update(b);remaining-=len(b)
assert raw.hexdigest()==audit['raw_snapshot_sha256']
proof={'status':'PASS','at':datetime.datetime.now().astimezone().isoformat(),'old_telemetry_bound':bound,'preserved_rows':count,'old_sha256':cold['history_before']['sha256'],'final_sha256':h.hexdigest(),'quick_check':check,'pending_commands':pending,'open_experiments':opened,'final_counts':counts,'formal_raw_mqtt_prefix_bytes':size,'formal_raw_mqtt_prefix_sha256':raw.hexdigest(),'audit_sha256':hashlib.sha256((q/'analysis-final.json').read_bytes()).hexdigest(),'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(e/'history-preserved-final.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
