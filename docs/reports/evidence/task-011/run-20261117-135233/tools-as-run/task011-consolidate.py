from pathlib import Path
import json,os,signal,subprocess,time,socket
S=json.loads(Path('/tmp/task011-active.json').read_text());QA=Path(S['qa']);OUT=Path(S['evidence']);profiles=[str(QA/f'node_0{i}-profile') for i in (1,2,3)];owned=[]
for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:cmd=(p/'cmdline').read_bytes().decode().replace('\0',' ')
    except (OSError,UnicodeError):continue
    if any(profile in cmd for profile in profiles) and '--type=' not in cmd and 'crashpad' not in cmd and os.getpgid(int(p.name))==int(p.name):owned.append(int(p.name))
assert len(owned)==3,owned
for pid in owned:os.killpg(pid,signal.SIGTERM)
profile=QA/'vscode-shared-profile';(profile/'User').mkdir(parents=True,exist_ok=True)
(profile/'User/settings.json').write_text(json.dumps({'workbench.startupEditor':'none','update.mode':'none','extensions.autoUpdate':False,'extensions.autoCheckUpdates':False,'security.workspace.trust.enabled':False,'window.restoreWindows':'none','workbench.secondarySideBar.defaultVisibility':'hidden','wokwi.hidePersonalInfo':True,'chat.disableAIFeatures':True}))
args=['/usr/share/code/code','--new-window','--user-data-dir='+str(profile),'--extensions-dir='+str(QA/'extensions'),'--remote-debugging-port=19226','--skip-welcome','--skip-release-notes']
records=json.loads((QA/'owned-processes.json').read_text())
for n in (1,2,3):
    full=args+[str(QA/f'node_0{n}')];p=subprocess.Popen(full,stdout=(OUT/f'vscode-shared-{n}.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
    records.append({'name':f'vscode-shared-{n}','pid':p.pid,'args':full,'proc_start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21]})
    if n==1:
        for i in range(60):
            with socket.socket() as sock:
                if sock.connect_ex(('127.0.0.1',19226))==0:break
            time.sleep(.25)
    time.sleep(1)
(QA/'owned-processes.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'qa-runtime-consolidation.json').write_text(json.dumps({'old_owned_groups_stopped':owned,'new_profile':str(profile),'cdp_port':19226,'reason':'Three independent VS Code profiles consume unnecessary main/GPU/background processes; use independent windows sharing one QA process. Firmware/timers/schema unchanged.','old_latency_results_preserved':'latency-trials.json','new_launches':records[-3:]},indent=2)+'\n');print('Consolidated owned VS Code runtime; three windows, one QA profile, CDP19226')
