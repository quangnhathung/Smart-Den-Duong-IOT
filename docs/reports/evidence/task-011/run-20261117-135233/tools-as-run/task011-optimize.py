from pathlib import Path
import json,os,signal,subprocess,time,socket
S=json.loads(Path('/tmp/task011-active.json').read_text());QA=Path(S['qa']);OUT=Path(S['evidence']);groups=[]
for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:cmd=(p/'cmdline').read_bytes().decode().replace('\0',' ')
    except (OSError,UnicodeError):continue
    if str(QA) in cmd and '--user-data-dir' in cmd and '--type=' not in cmd and 'crashpad' not in cmd and os.getpgid(int(p.name))==int(p.name):groups.append(int(p.name))
assert len(groups)<=3,groups
for pid in groups:os.killpg(pid,signal.SIGTERM)
for attempt in range(100):
    free=[]
    for port in (19222,19223,19224):
        with socket.socket() as sock:free.append(sock.connect_ex(('127.0.0.1',port))!=0)
    if all(free):break
    time.sleep(.1)
else:raise RuntimeError('Owned debug ports did not close')
owned=json.loads((QA/'owned-processes.json').read_text());extra=['--disable-background-timer-throttling=true','--disable-renderer-backgrounding=true','--disable-backgrounding-occluded-windows=true']
for n in (1,2,3):
    profile=QA/f'node_0{n}-final-profile';(profile/'User').mkdir(parents=True,exist_ok=True)
    (profile/'User/settings.json').write_text(json.dumps({'workbench.startupEditor':'none','update.mode':'none','extensions.autoUpdate':False,'extensions.autoCheckUpdates':False,'security.workspace.trust.enabled':False,'window.restoreWindows':'none','workbench.secondarySideBar.defaultVisibility':'hidden','wokwi.hidePersonalInfo':True,'chat.disableAIFeatures':True}))
    args=['/usr/share/code/code','--new-window','--user-data-dir='+str(profile),'--extensions-dir='+str(QA/'extensions'),'--remote-debugging-port='+str(19221+n),'--skip-welcome','--skip-release-notes','--folder-uri='+ (QA/f'node_0{n}').as_uri(),*extra]
    p=subprocess.Popen(args,stdout=(OUT/f'vscode-final-{n}.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True);owned.append({'name':f'vscode-optimized-{n}','pid':p.pid,'args':args,'proc_start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21]})
(QA/'owned-processes.json').write_text(json.dumps(owned,indent=2)+'\n')
(OUT/'qa-runtime-final.json').write_text(json.dumps({'shared_group_stopped':groups,'runtime':'Three independent QA profiles; background throttling disabled; AI features disabled only in QA profiles','flags':extra,'reason':'Shared VSCode runtime measured about 37% simulation speed; revert process isolation, avoid background scheduling throttling. No product code/timer change.','launches':owned[-3:]},indent=2)+'\n');print('Launched independent QA processes with background throttling disabled')
