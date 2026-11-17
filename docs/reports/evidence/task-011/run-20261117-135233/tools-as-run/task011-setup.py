import json,os,subprocess,socket,shutil
from pathlib import Path
S=json.loads(Path('/tmp/task011-active.json').read_text());ROOT=Path(S['root']);QA=Path(S['qa']);OUT=Path(S['evidence'])
ports=[1883,8001,5500,4000,4001,4002,19222,19223,19224,18771]
for port in ports:
    with socket.socket() as sock:sock.bind(('127.0.0.1',port))
(OUT/'qa-port-preflight.json').write_text(json.dumps({'free_ports':ports})+'\n')
owned=[]
def start(name,args,cwd=None,env=None):
    log=(OUT/(name+'.log')).open('w');p=subprocess.Popen(args,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    owned.append({'name':name,'pid':p.pid,'args':args,'proc_start_ticks':Path(f'/proc/{p.pid}/stat').read_text().split()[21]})
    (QA/'owned-processes.json').write_text(json.dumps(owned,indent=2)+'\n');return p
conf=QA/'mosquitto.conf';conf.write_text('listener 1883 0.0.0.0\nallow_anonymous true\npersistence false\nlog_dest stdout\nconnection_messages true\n')
name='smartlight-task011-'+OUT.name
p=subprocess.run(['docker','run','-d','--name',name,'--label','smartlight.qa='+OUT.name,'-p','127.0.0.1:1883:1883','--mount',f'type=bind,src={conf},dst=/mosquitto/config/mosquitto.conf,readonly','eclipse-mosquitto:2.1.2-alpine'],capture_output=True,text=True,check=True)
(OUT/'owned-broker.json').write_text(json.dumps({'name':name,'container_id':p.stdout.strip(),'label':OUT.name,'port':1883},indent=2)+'\n')
# Reuse installed runtimes only. No download or credential handling.
env=dict(os.environ);env.update(SMARTLIGHT_DB=str(QA/'qa.db'),SMARTLIGHT_MQTT_HOST='127.0.0.1',SMARTLIGHT_MQTT_PORT='1883',PYTHONDONTWRITEBYTECODE='1')
start('backend',[str(ROOT.parent/'backend/.venv/bin/python'),'-B','-m','uvicorn','smartlight.api:app','--host','127.0.0.1','--port','8001','--workers','1'],ROOT.parent/'backend',env)
source=ROOT.parent/'dashboard';dest=QA/'dashboard';hashes={}
import hashlib
for path in source.rglob('*'):
    rel=path.relative_to(source)
    if not path.is_file() or any(x in rel.parts for x in ('.git','node_modules','output','.playwright-cli')):continue
    target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target);hashes[str(rel)]=hashlib.sha256(path.read_bytes()).hexdigest()
config=dest/'config.js';config.write_text(config.read_text().replace('http://127.0.0.1:8000','http://127.0.0.1:8001'))
(OUT/'dashboard-qa-source.json').write_text(json.dumps({'source':str(source),'qa_copy':str(dest),'source_sha256':hashes,'runtime_change':'Only API URL in QA config.js:8001'},indent=2)+'\n')
server=QA/'live.cjs';server.write_text("const server=require('/home/quangnhathung/.vscode/extensions/ritwickdey.liveserver-5.7.10/node_modules/live-server');server.start({root:"+json.dumps(str(dest))+",host:'127.0.0.1',port:5500,open:false,logLevel:1});process.on('SIGTERM',()=>{server.shutdown();process.exit(0)});\n")
start('liveserver',['node',str(server)])
ext=QA/'extensions';ext.mkdir();(ext/'wokwi.wokwi-vscode-4.1.0').symlink_to(Path.home()/'.vscode/extensions/wokwi.wokwi-vscode-4.1.0',target_is_directory=True)
for n in range(1,4):
    node=f'node_0{n}';project=QA/node;project.mkdir();shutil.copyfile(ROOT/'simulations'/node/'diagram.json',project/'diagram.json');shutil.copyfile(ROOT/'simulations'/node/'wokwi.toml',project/'wokwi.toml');shutil.copytree(ROOT/'simulations'/node/'build',project/'build')
    profile=QA/(node+'-profile');user=profile/'User';user.mkdir(parents=True)
    (user/'settings.json').write_text(json.dumps({'workbench.startupEditor':'none','update.mode':'none','extensions.autoUpdate':False,'extensions.autoCheckUpdates':False,'security.workspace.trust.enabled':False,'window.restoreWindows':'none','workbench.secondarySideBar.defaultVisibility':'hidden','wokwi.hidePersonalInfo':True}))
    start('vscode-'+node,['/usr/share/code/code','--new-window','--user-data-dir='+str(profile),'--extensions-dir='+str(ext),'--remote-debugging-port='+str(19221+n),'--no-first-run','--skip-welcome','--skip-release-notes',str(project)])
    (QA/(node+'-playwright.json')).write_text(json.dumps({'browser':{'cdpEndpoint':f'http://127.0.0.1:{19221+n}'}}))
print('Started owned QA broker/backend/LiveServer and three isolated Wokwi windows. Ownership saved in',QA)
