import json,os,signal,socket,subprocess,time,sqlite3,hashlib
from pathlib import Path
from datetime import datetime,timezone
S=json.loads(Path('/tmp/task011-active.json').read_text());QA=Path(S['qa']);OUT=Path(S['evidence'])
summary=json.loads((OUT/'stability-02/summary.json').read_text());assert summary['status']=='PASS' and summary['elapsed_seconds']>=1800
# Capture database before stopping services. No destructive changes or checkpoints on the live DB.
with sqlite3.connect('file:'+str(QA/'qa.db')+'?mode=ro',uri=True) as db:
    tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")};counts={t:db.execute('SELECT count(*) FROM '+t).fetchone()[0] for t in sorted(tables) if t.isidentifier()}
    check=db.execute('PRAGMA quick_check').fetchone()[0];assert check=='ok'
    columns=[r[1] for r in db.execute('PRAGMA table_info(commands)')]
    state='result' if 'result' in columns else 'status';pending=db.execute('SELECT count(*) FROM commands WHERE '+state+"='PENDING'").fetchone()[0];assert pending==0,pending
    open_experiments=db.execute('SELECT count(*) FROM experiments WHERE ended_at IS NULL').fetchone()[0];assert open_experiments==0
    backup=QA/'qa-final.db'
    with sqlite3.connect(backup) as dest:db.backup(dest)
(OUT/'database-final.json').write_text(json.dumps({'quick_check':check,'counts':counts,'pending_commands':pending,'open_experiments':open_experiments,'backup_path':str(backup),'backup_sha256':hashlib.sha256(backup.read_bytes()).hexdigest()},indent=2)+'\n')
owned=json.loads((QA/'owned-processes.json').read_text());signals=[]
def stop(pid,reason,start_ticks=None):
    p=Path(f'/proc/{pid}')
    if not p.exists():return
    if start_ticks and (p/'stat').read_text().split()[21]!=start_ticks:return
    cmd=(p/'cmdline').read_bytes().decode(errors='replace')
    if not cmd:return
    os.kill(pid,signal.SIGTERM);signals.append({'pid':pid,'reason':reason})
# These two controllers are unique scripts created by this task; do not stop any other node/chrome process.
for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:args=(p/'cmdline').read_bytes().decode().split('\0')
    except (OSError,UnicodeError):continue
    if any(script in args[1:] for script in ('/tmp/task011-ui.cjs','/tmp/task011-dashboard.cjs')):stop(int(p.name),'owned QA UI controller')
for record in reversed(owned):
    if record['name'] in ('backend','observer','observer-fast','liveserver','serial-observer','serial-observer-v2'):
        stop(record['pid'],record['name'],record['proc_start_ticks'])
# Isolated VS Code main processes are proven by the exact QA root and an owned process group.
for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:cmd=(p/'cmdline').read_bytes().decode().replace('\0',' ')
    except (OSError,UnicodeError):continue
    pid=int(p.name)
    if str(QA) in cmd and '--user-data-dir' in cmd and '--type=' not in cmd and 'crashpad' not in cmd and os.getpgid(pid)==pid:
        os.killpg(pid,signal.SIGTERM);signals.append({'group':pid,'reason':'owned isolated VS Code QA profile'})
# Ensure our own launched dashboard Chrome is not orphaned; never close the user's browser.
chrome=json.loads((OUT/'owned-dashboard-browser.json').read_text())['chrome_pid'];p=Path(f'/proc/{chrome}/cmdline')
if p.exists() and b'--remote-debugging-port=19225' in p.read_bytes():stop(chrome,'owned Playwright dashboard Chrome')
broker=json.loads((OUT/'owned-broker.json').read_text());label=subprocess.check_output(['docker','inspect','--format','{{index .Config.Labels "smartlight.qa"}}',broker['name']],text=True).strip();assert label==broker['label']
logs=subprocess.run(['docker','logs','--timestamps',broker['name']],capture_output=True,text=True,check=True);(OUT/'broker-final.log').write_text(logs.stdout+logs.stderr)
subprocess.run(['docker','stop','-t','1',broker['name']],capture_output=True,check=True)
ports=[1883,8001,5500,4000,4001,4002,19222,19223,19224,19225,19226,18771,18772,18773]
for attempt in range(50):
    active=[]
    for port in ports:
        with socket.socket() as sock:
            sock.settimeout(.2)
            if sock.connect_ex(('127.0.0.1',port))==0:active.append(port)
    if not active:break
    time.sleep(.1)
result={'completed_at':datetime.now(timezone.utc).isoformat(),'status':'PASS' if not active else 'INCOMPLETE','signals':signals,'owned_broker_stopped':broker['name'],'container_retained_stopped_for_traceability':True,'ports_checked':ports,'still_listening_ports':active,'qa_data_retained':str(QA),'user_services_and_databases':'not stopped or modified'}
(OUT/'cleanup.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert not active
