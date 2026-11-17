from pathlib import Path
import json,os,signal,subprocess,time,shutil,socket
s=json.loads(Path('/tmp/task011-active.json').read_text());qa=Path(s['qa']);out=Path(s['evidence']);a=json.loads((qa/'owned-processes.json').read_text());old=next(x for x in a if x['name']=='vscode-node_01')
matched=[]
for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:cmd=(p/'cmdline').read_bytes().decode().replace('\0',' ')
    except (OSError,UnicodeError):continue
    if str(qa/'node_01-profile') in cmd and '--type=' not in cmd and 'crashpad' not in cmd and os.getpgid(int(p.name))==int(p.name):matched.append(int(p.name))
assert len(matched)==1,matched
os.killpg(matched[0],signal.SIGTERM)
for i in range(40):
    with socket.socket() as sock:
        if sock.connect_ex(('127.0.0.1',19222))!=0:break
    time.sleep(.1)
profile=qa/'node_01-profile-recovered';(profile/'User').mkdir(parents=True,exist_ok=True);shutil.copyfile(qa/'node_01-profile/User/settings.json',profile/'User/settings.json')
args=[x.replace(str(qa/'node_01-profile'),str(profile)) for x in old['args']]
proc=subprocess.Popen(args,stdout=(out/'vscode-node_01-recovered2.log').open('w'),stderr=subprocess.STDOUT,start_new_session=True)
a.append({'name':'vscode-node_01-recovered2','pid':proc.pid,'args':args,'proc_start_ticks':Path(f'/proc/{proc.pid}/stat').read_text().split()[21]})
(qa/'owned-processes.json').write_text(json.dumps(a,indent=2)+'\n');print('Restarted owned browser group',matched[0], 'new pid',proc.pid)
