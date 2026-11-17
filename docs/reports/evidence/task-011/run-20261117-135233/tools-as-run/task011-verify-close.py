from pathlib import Path
from datetime import datetime, timezone
import ast,gzip,hashlib,json,re,sqlite3,subprocess
s=json.loads(Path('/tmp/task011-active.json').read_text());root=Path(s['root']);qa=Path(s['qa']);out=Path(s['evidence']);baseline=json.loads((qa/'baseline.json').read_text())
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(p):return sha(p.read_bytes())
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
preservation={}
for name in ['backend','dashboard']:
 repo=root.parent/name;b=baseline[name];status=subprocess.check_output(['git','status','--porcelain'],cwd=repo,text=True)
 mismatches=[p for p,h in b['hashes'].items() if not (repo/p).is_file() or file_sha(repo/p)!=h]
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
 preservation[name]={'mismatched_original_tracked_paths':mismatches,'status':status,'original_status':b['status'],'head':head,'original_head':b['head']}
 assert not mismatches and status==b['status'] and head==b['head'],preservation[name]
protected=['docs/srs.md','src/LightingController.cpp','src/LightingController.h','src/ControlConfig.h','src/DimmingController.cpp','src/DimmingController.h','src/FaultDetector.cpp','src/FaultDetector.h','src/SensorReader.cpp','src/SensorReader.h','src/main.cpp']
preservation['protected_firmware']={p:file_sha(root/p)==baseline['firmware']['hashes'][p] for p in protected};assert all(preservation['protected_firmware'].values())
old_evidence=[p for p in baseline['firmware']['hashes'] if p.startswith('docs/reports/evidence/')]
mismatches=[p for p in old_evidence if file_sha(root/p)!=baseline['firmware']['hashes'][p]];assert not mismatches,mismatches
preservation['historical_tracked_evidence']={'checked':len(old_evidence),'mismatches':mismatches}
# The specification folder existed before this run and is now tracked; compare to its first commit.
spec='docs/reports/evidence/task-011/specification-20261117-131925'
first=subprocess.check_output(['git','log','--reverse','--format=%H','--',spec],cwd=root,text=True).splitlines()[0]
spec_files=subprocess.check_output(['git','ls-tree','-r','--name-only',first,'--',spec],cwd=root,text=True).splitlines()
assert spec_files
for p in spec_files:assert (root/p).read_bytes()==subprocess.check_output(['git','show',first+':'+p],cwd=root),p
preservation['specification_evidence']={'first_commit':first,'checked':len(spec_files),'unchanged':True}
for f in ['report.md','checklists.md']:
 old=(qa/f).read_bytes();new=(root/'docs/reports'/f).read_bytes();assert new.endswith(old) and len(new)>len(old)
 preservation[f]={'original_tail_bytes':len(old),'original_tail_sha256':sha(old),'preserved':True}
for copy,original in [('task-010-before.md','task.md'),('task-011-accepted.md','next-task.md')]:
 assert (out/copy).read_bytes()==(qa/original).read_bytes()
preservation['archived_tasks_exact']=True
# Bind shipped inputs and artifacts to the final built/simulated versions.
inputs={};artifacts={}
for node in ['node_01','node_02','node_03']:
 m=json.loads((out/(node+'-artifact-manifest-final.json')).read_text())
 for p,h in m['inputs_sha256'].items():assert file_sha(root/p)==h,(node,p);inputs[p]=h
 for name,entry in m['artifacts'].items():
  assert file_sha(root/entry['source'])==entry['sha256'] and file_sha(root/entry['target'])==entry['sha256'],(node,name)
 artifacts[node]={n:v['sha256'] for n,v in m['artifacts'].items()}
preservation['final_built_inputs']={'checked':len(inputs),'match_final_manifests':True}
preservation['artifacts']=artifacts
dump(out/'source-preservation-final.json',preservation)
archives=json.loads((out/'archives.json').read_text());decompressed={}
for entry in archives['files']:
 p=out/entry['archive'];data=gzip.decompress(p.read_bytes());assert len(data)==entry['raw_bytes'] and sha(data)==entry['raw_sha256'] and file_sha(p)==entry['gzip_sha256']
 assert Path(entry['original_local_copy']).read_bytes()==data
 if entry['original'].endswith('.jsonl'):
  for line in data.splitlines():json.loads(line)
 decompressed[entry['original']]=data
# Offline recheck of the fixed full interval against the frozen SQLite backup.
start=json.loads((out/'stability-02/start.json').read_text());audit=json.loads((out/'stability-02/wire-audit.json').read_text());begin=start['start_monotonic_ns'];end=begin+1800*10**9
assert audit['start_monotonic_ns']==begin and audit['end_monotonic_ns']==end
all_events=[]
for f in ['mqtt-events.jsonl','mqtt-events-fast.jsonl']:
 all_events.extend(json.loads(l) for l in decompressed[f].splitlines())
window=[e for e in all_events if begin<=e['monotonic_ns']<=end]
assert not [e for e in window if e['event'] in ['connected','disconnected']]
assert not [e for e in window if e.get('topic','').endswith('/command')]
assert not [e for e in window if e.get('topic','').endswith('/availability') and e['payload'].get('status')=='OFFLINE']
dbinfo=json.loads((out/'database-final.json').read_text());dbpath=Path(dbinfo['backup_path']);assert file_sha(dbpath)==dbinfo['backup_sha256']
db=sqlite3.connect('file:'+str(dbpath)+'?mode=ro',uri=True);db.row_factory=sqlite3.Row;assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
counts={}
for node,boot in start['boots'].items():
 stream=[e for e in all_events if e.get('topic','').endswith('/'+node+'/telemetry')]
 before=[e for e in stream if e['monotonic_ns']<begin][-1];after=[e for e in stream if e['monotonic_ns']>end][0];within=[e for e in stream if begin<=e['monotonic_ns']<=end]
 assert all(e['payload']['node_id']==node and e['payload']['boot_id']==boot and e['payload']['mode']=='AUTO' and not e['payload']['faults'] for e in within)
 series=[before]+within+[after];seq=[int(e['payload']['seq']) for e in series];up=[int(e['payload']['uptime_ms']) for e in series]
 assert all(b==a+1 for a,b in zip(seq,seq[1:])) and all(b>a for a,b in zip(up,up[1:]))
 assert max((b['monotonic_ns']-a['monotonic_ns'])/1e9 for a,b in zip(series,series[1:]))<10
 stored={int(r['seq']):dict(r) for r in db.execute('SELECT * FROM telemetry WHERE node_id=? AND boot_id=?',(node,boot))};continuity=set()
 for e in within:
  r=stored[int(e['payload']['seq'])];assert r['quality']=='ACCEPTED' and json.loads(r['payload'])==e['payload'];continuity.add(r['continuity'])
 assert len(continuity)==1 and sorted(continuity)==audit['nodes'][node]['continuity_keys']
 assert len(within)==audit['nodes'][node]['received_messages'];counts[node]=len(within)
db.close();assert sum(counts.values())==5360
lat=json.loads((out/'latency-final-audit.json').read_text());assert file_sha(out/lat['source'])==lat['source_sha256'];assert all(v['samples']==10 and v['pass']==10 for v in lat['by_node'].values())
# JSON syntax throughout evidence, excluding compressed streams already checked.
json_count=0
for p in out.rglob('*.json'):
 if p.name in ['manifest.json','verification.json']:continue
 json.loads(p.read_text());json_count+=1
# Current/new links only: byte-preserved historical Markdown has original path context.
paths=[root/'README.md',root/'docs/reports/task.md',root/'docs/reports/next-task.md',out/'README.md',out/'tools-as-run/README.md']+[root/'docs/techs'/f'{n}.md' for n in ['architecture','firmware','mqtt','simulation','testing','backend','dashboard']]
texts=[(p,p.read_text()) for p in paths]+[(root/'docs/reports'/f,(root/'docs/reports'/f).read_bytes()[:-(len((qa/f).read_bytes()))].decode()) for f in ['report.md','checklists.md']]
link_count=0;missing=[]
for p,t in texts:
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t):
  if re.match(r'^[a-z]+:',target) or target.startswith('#'):continue
  target=target.split('#')[0].strip('<>')
  if not target:continue
  link_count+=1
  if not (p.parent/target).exists() and p.parent/target not in [out/'manifest.json',out/'verification.json']:missing.append({'document':str(p.relative_to(root)),'target':target})
assert not missing,missing
for p in out.rglob('*'):
 if p.is_file():assert p.suffix.lower() not in ['.db','.sqlite','.sqlite3','.bin','.elf'],str(p)
# Whitespace check of current tracked changes, with archived streams represented by lossless gzip.
whitespace=subprocess.run(['git','diff','--check'],cwd=root,text=True,capture_output=True);assert whitespace.returncode==0,whitespace.stdout+whitespace.stderr
# Manifest excludes itself and verification to avoid circular hashes.
manifest={str(p.relative_to(out)):{'bytes':p.stat().st_size,'sha256':file_sha(p)} for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ['manifest.json','verification.json']}
dump(out/'manifest.json',{'algorithm':'SHA256','excluded':['manifest.json','verification.json'],'files':manifest})
for p,v in manifest.items():assert file_sha(out/p)==v['sha256']
verification={'status':'PASS','checked_at':datetime.now(timezone.utc).isoformat(),'scope':'Evidence integrity/history/source preservation and offline recheck; functional tests remain separately documented','report_old_bytes_preserved':True,'checklist_old_bytes_preserved':True,'archived_tasks_exact':True,'sibling_sources_and_status_preserved':True,'protected_firmware_unchanged':True,'final_build_inputs_and_artifact_hashes_match':True,'historical_tracked_evidence_unchanged':len(old_evidence),'specification_evidence_unchanged':len(spec_files),'gzip_raw_streams_verified':len(archives['files']),'offline_fixed_window_seconds':1800,'offline_sqlite_matching_messages':counts,'offline_all_window_boots_sequences_uptimes_and_boundaries_verified':True,'latency_raw_sha_matches_audit':True,'json_files_parsed':json_count,'internal_links_checked':link_count,'missing_links':missing,'no_database_or_build_artifacts_in_evidence':True,'git_diff_check':'PASS','manifest_files':len(manifest),'manifest_sha256':file_sha(out/'manifest.json'),'known_incomplete':['stability-01','stability-02 HTTP/resource probe received SIGTERM143; full interval verified independently','original latency flags due to100k label parser retained']}
dump(out/'verification.json',verification)
for p,t in texts:
 for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',t):
  if re.match(r'^[a-z]+:',target) or target.startswith('#'):continue
  target=target.split('#')[0].strip('<>')
  if target:assert (p.parent/target).exists(),(p,target)
print(json.dumps(verification,ensure_ascii=False))
