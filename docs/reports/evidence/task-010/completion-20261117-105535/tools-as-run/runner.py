"""TASK-010 runner: bounded QA commands only. Never print credential values."""
import argparse,json,os,re,shlex,subprocess,sys,time,select,socket,hashlib
from pathlib import Path
STATE=json.loads(Path('/tmp/task010-completion/state.json').read_text());ROOT=Path(STATE['root']);OUT=Path(STATE['evidence']);WORK=Path('/tmp/task010-completion');CLI=Path.home()/'.wokwi/bin/wokwi-cli'
def cli_env():
 env=dict(os.environ)
 if not env.get('WOKWI_CLI_TOKEN'):
  for line in (Path.home()/'.bashrc').read_text().splitlines():
   if re.match(r'^\s*(?:export\s+)?WOKWI_CLI_TOKEN\s*=',line):
    pieces=shlex.split(line,comments=True)
    assignment=next((x for x in pieces if x.startswith('WOKWI_CLI_TOKEN=')),None)
    if assignment:
     value=assignment.split('=',1)[1]
     if not value or '$' in value or '`' in value:raise RuntimeError('Token assignment requires interactive shell loading; not evaluated by this runner')
     env['WOKWI_CLI_TOKEN']=value
 if not env.get('WOKWI_CLI_TOKEN'):raise RuntimeError('WOKWI_CLI_TOKEN unavailable')
 return env
def save(name,value):
 p=OUT/name
 if p.exists():raise RuntimeError('Evidence exists: '+name)
 p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def preflight():
 ports={}
 for port in [1883,11883,11884,19011,8001,5500,4000,18765]:
  s=socket.socket()
  try:s.bind(('127.0.0.1',port));ports[str(port)]='free'
  except OSError as e:ports[str(port)]='unavailable: '+str(e)
  finally:s.close()
 env=cli_env();p=subprocess.Popen([str(CLI),'mcp','--quiet',str(ROOT/'simulations/node_01')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
 messages=[];errors=[];tools=[]
 def send(v):p.stdin.write(json.dumps(v)+'\n');p.stdin.flush()
 try:
  send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'task010-qa','version':'1'}}})
  end=time.monotonic()+12
  while time.monotonic()<end:
   streams,_,_=select.select([p.stdout,p.stderr],[],[],max(0,end-time.monotonic()))
   if not streams:break
   for stream in streams:
    line=stream.readline()
    if not line:continue
    line=line.replace(env['WOKWI_CLI_TOKEN'],'<REDACTED>')
    if stream==p.stderr:errors.append(line.strip());continue
    try:value=json.loads(line)
    except ValueError:errors.append(line.strip());continue
    messages.append(value)
    if value.get('id')==1:
     send({'jsonrpc':'2.0','method':'notifications/initialized'});send({'jsonrpc':'2.0','id':2,'method':'tools/list'})
    if value.get('id')==2:tools=value.get('result',{}).get('tools',[]);end=0;break
 finally:
  if p.poll() is None:p.terminate()
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 result={'ports':ports,'cli':subprocess.run([str(CLI),'--version'],capture_output=True,text=True).stdout.strip(),'token_source':'existing .bashrc WOKWI_CLI_TOKEN; value omitted','mcp_tools':tools,'mcp_messages':messages,'errors':errors,'artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'.pio/build/esp32dev/firmware.bin',ROOT/'.pio/build/esp32dev/firmware.elf',ROOT/'simulations/node_01/build/firmware.bin',ROOT/'simulations/node_01/build/firmware.elf']}}
 save('preflight.json',result);print(json.dumps({'ports':ports,'cli':result['cli'],'mcp_tools':[x['name'] for x in tools],'errors':errors},ensure_ascii=False))

def request(path,value=None,timeout=55):
 from urllib.request import Request,urlopen
 body=json.dumps(value).encode() if value is not None else None
 with urlopen(Request('http://127.0.0.1:18765'+path,data=body,headers={'Content-Type':'application/json'}),timeout=timeout) as r:return json.loads(r.read())
def infra_up():
 name='smartlight-task010-'+OUT.name.split('-',1)[1];conf=WORK/'mosquitto.conf';conf.write_text('listener 1883 0.0.0.0\nallow_anonymous true\npersistence false\nlog_dest stdout\nconnection_messages true\n')
 command=['docker','run','-d','--name',name,'--label','smartlight.qa='+OUT.name,'-p','127.0.0.1:11884:1883','--mount','type=bind,src='+str(conf)+',dst=/mosquitto/config/mosquitto.conf,readonly','eclipse-mosquitto:2.1.2-alpine']
 result=subprocess.run(command,check=True,text=True,capture_output=True);save('owned-broker.json',{'name':name,'container_id':result.stdout.strip(),'port':11884,'label':OUT.name})
 log=(OUT/'controller.log').open('x');p=subprocess.Popen([str(ROOT.parent/'backend/.venv/bin/python'),'-B',str(WORK/'controller.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,cwd=WORK);save('owned-controller.json',{'pid':p.pid,'script':str(WORK/'controller.py')})
 print('Started owned broker',name,'controller pid',p.pid)
def cli_probe():
 result=request('/mcp',{'name':'wokwi_start_simulation','arguments':{'projectPath':str(ROOT/'simulations/node_01')}});save('cli-start.json',result);print(json.dumps(result))
 if result['response'].get('error') or result['response'].get('result',{}).get('isError'):return
 readings=[];deadline=time.monotonic()+32
 while time.monotonic()<deadline:
  result=request('/mcp',{'name':'wokwi_read_serial','arguments':{'clear':True}});readings.append(result);print(json.dumps(result)[-1900:]);state=request('/state')
  if state['latest']:break
  time.sleep(3)
 result={'latest':request('/state')['latest'],'readings':readings,'note':'Actual CLI simulation network preflight; no telemetry relay or fixture'};save('cli-network-probe.json',result);print('LOCAL_MQTT_REACHED',bool(result['latest']))
 request('/mcp',{'name':'wokwi_stop_simulation','arguments':{}})

def web_up():
 import shutil
 dest=WORK/'dashboard';original={}
 for source in (ROOT.parent/'dashboard').rglob('*'):
  relative=source.relative_to(ROOT.parent/'dashboard')
  if not source.is_file() or any(x in relative.parts for x in ['.git','node_modules','output','.playwright-cli']):continue
  target=dest/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);original[str(relative)]=hashlib.sha256(source.read_bytes()).hexdigest()
 config=dest/'config.js';config.write_text(config.read_text().replace('http://127.0.0.1:8000','http://127.0.0.1:8001'))
 save('dashboard-qa-source.json',{'source':str(ROOT.parent/'dashboard'),'root':str(dest),'original_sha256':original,'only_runtime_configuration_changed':'config.js API8001; other runtime files match source'})
 env=dict(os.environ);env.update(SMARTLIGHT_DB=str(WORK/'qa.db'),SMARTLIGHT_MQTT_HOST='127.0.0.1',SMARTLIGHT_MQTT_PORT='11883')
 log=(OUT/'backend-qa.log').open('x');p=subprocess.Popen([str(ROOT.parent/'backend/.venv/bin/python'),'-B','-m','uvicorn','smartlight.api:app','--host','127.0.0.1','--port','8001','--workers','1'],cwd=ROOT.parent/'backend',env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-backend.json',{'pid':p.pid,'database':str(WORK/'qa.db'),'port':8001})
 log=(OUT/'liveserver.log').open('x');p=subprocess.Popen(['node',str(WORK/'live.cjs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-liveserver.json',{'pid':p.pid,'root':str(dest),'port':5500})
 print('Started backend QA8001 and LiveServer5500; original repos unchanged')

def vscode_up():
 project=WORK/'wokwi-project';project.mkdir(exist_ok=True)
 (project/'wokwi.toml').write_text("[wokwi]\nversion=1\nfirmware='"+str(ROOT/'.pio/build/esp32dev/firmware.bin')+"'\nelf='"+str(ROOT/'.pio/build/esp32dev/firmware.elf')+"'\nrfc2217ServerPort=4000\n")
 (project/'diagram.json').symlink_to(ROOT/'simulations/node_01/diagram.json')
 settings=project/'.vscode';settings.mkdir();(settings/'settings.json').write_text(json.dumps({'workbench.startupEditor':'none','update.mode':'none','extensions.autoUpdate':False,'extensions.autoCheckUpdates':False,'security.workspace.trust.enabled':False,'window.restoreWindows':'none'}))
 profile=WORK/'vscode-profile';log=(OUT/'vscode-qa.log').open('x')
 args=['/usr/share/code/code','--new-window','--user-data-dir='+str(profile),'--extensions-dir='+str(Path.home()/'.vscode/extensions'),'--remote-debugging-port=19222','--no-first-run','--skip-welcome','--skip-release-notes',str(project)]
 proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-vscode.json',{'pid':proc.pid,'profile':str(profile),'project':str(project),'cdp_port':19222})
 (WORK/'vscode-playwright.json').write_text(json.dumps({'browser':{'cdpEndpoint':'http://127.0.0.1:19222'}}))
 print('Started isolated VSCode QA profile pid',proc.pid)

def vscode_isolate():
 import signal
 old=json.loads((OUT/'owned-vscode.json').read_text());os.kill(old['pid'],signal.SIGTERM);time.sleep(1)
 project=WORK/'wokwi-project';(project/'.vscode/settings.json').write_text(json.dumps({'workbench.startupEditor':'none'}))
 profile=WORK/'vscode-profile';(profile/'User/settings.json').write_text(json.dumps({'workbench.startupEditor':'none','update.mode':'none','extensions.autoUpdate':False,'extensions.autoCheckUpdates':False,'security.workspace.trust.enabled':False,'window.restoreWindows':'none','workbench.secondarySideBar.defaultVisibility':'hidden'}))
 extensions=WORK/'vscode-extensions';extensions.mkdir();(extensions/'wokwi.wokwi-vscode-4.1.0').symlink_to(Path.home()/'.vscode/extensions/wokwi.wokwi-vscode-4.1.0',target_is_directory=True)
 log=(OUT/'vscode-isolated.log').open('x');args=['/usr/share/code/code','--new-window','--user-data-dir='+str(profile),'--extensions-dir='+str(extensions),'--remote-debugging-port=19222','--no-first-run','--skip-welcome','--skip-release-notes',str(project)]
 proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-vscode-isolated.json',{'pid':proc.pid,'profile':str(profile),'project':str(project),'cdp_port':19222});print('Isolated Wokwi-only VSCode pid',proc.pid)

def controller_restart():
 request('/stop',{})
 old=json.loads((OUT/'owned-controller.json').read_text());deadline=time.monotonic()+8
 while time.monotonic()<deadline:
  try:os.kill(old['pid'],0)
  except ProcessLookupError:break
  time.sleep(.1)
 log=(OUT/'controller-v2.log').open('x');p=subprocess.Popen([str(ROOT.parent/'backend/.venv/bin/python'),'-B',str(WORK/'controller.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True,cwd=WORK);save('owned-controller-v2.json',{'pid':p.pid,'script':str(WORK/'controller.py'),'reason':'QA proxy corrected from HTTP /commands assumption to actual MQTT /command; no production change'})
 print('Restarted owned controller with exact MQTT command topic',p.pid)

def serial_up():
 log=(OUT/'serial-observer.log').open('x');p=subprocess.Popen([str(Path.home()/'.platformio/penv/bin/python'),'-B',str(WORK/'serial_observer.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-serial.json',{'pid':p.pid});print('Started read-only RFC2217 observer',p.pid)

def service_control_up():
 log=(OUT/'service-control.log').open('x');p=subprocess.Popen([sys.executable,'-B',str(WORK/'service_control.py')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-service-control.json',{'pid':p.pid});print('Started guarded QA service controller',p.pid)

def backend_fix_publish():
 import shutil
 repo=ROOT.parent/'backend';expected=json.loads((WORK/'backend-original-service.json').read_text())['sha256']
 assert hashlib.sha256((repo/'smartlight/service.py').read_bytes()).hexdigest()==expected
 status=subprocess.run(['git','-C',str(repo),'status','--porcelain'],capture_output=True,text=True,check=True).stdout;assert not status
 branch='task/task-010-restart-sync';subprocess.run(['git','-C',str(repo),'switch','-c',branch],check=True)
 for name in ['smartlight/service.py','tests/test_service.py']:
  target=repo/name;shutil.copyfile(WORK/'backend-fix'/name,target)
  assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256((WORK/'backend-fix'/name).read_bytes()).digest()
 save('backend-fix-publication.json',{'branch':branch,'old_service_sha256':expected,'files':{name:hashlib.sha256((repo/name).read_bytes()).hexdigest() for name in ['smartlight/service.py','tests/test_service.py']},'committed':False})
 print('Published scoped backend fix on',branch,'with hash guards; no commit/push')
 print(request_service('/backend/restart'))
def request_service(path):
 from urllib.request import Request,urlopen
 with urlopen(Request('http://127.0.0.1:18766'+path,data=b'{}',headers={'Content-Type':'application/json'}),timeout=12) as r:return json.loads(r.read())

def latency_up():
 log=(OUT/'latency-controller.log').open('x');p=subprocess.Popen(['node',str(WORK/'latency.cjs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-latency-controller.json',{'pid':p.pid});print('Started latency controller',p.pid)

def latency_retry():
 import signal
 old=json.loads((OUT/'owned-latency-controller.json').read_text());os.kill(old['pid'],signal.SIGTERM)
 log=(OUT/'latency-controller-v2.log').open('x');p=subprocess.Popen(['node',str(WORK/'latency.cjs')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-latency-controller-v2.json',{'pid':p.pid});print('Using already-installed Google Chrome; latency controller',p.pid)

def video_up():
 args=['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-framerate','30','-video_size','1920x1040','-i',os.environ['DISPLAY']+'+0,0']
 subprocess.run(args+['-frames:v','1',str(OUT/'latency-desktop-before.png')],check=True,timeout=10)
 log=(OUT/'video-recorder.log').open('x');begin=time.time()*1000;p=subprocess.Popen(args+['-t','180','-c:v','libx264','-preset','superfast','-crf','30','-pix_fmt','yuv420p',str(OUT/'latency-side-by-side.mp4')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-video.json',{'pid':p.pid,'started_before_ms':begin,'started_after_ms':time.time()*1000,'crop':'1920x1040+0,0','fps':30,'limit_s':180});print('Started bounded QA side-by-side video',p.pid)

def opaque_windows():
 windows=json.loads((OUT/'latency-video-windows.json').read_text())
 for window in windows:
  subprocess.run(['xprop','-id',str(window['id']),'-f','_NET_WM_WINDOW_OPACITY','32c','-set','_NET_WM_WINDOW_OPACITY','4294967295'],check=True,capture_output=True)
 print('Set opaque property on the two owned QA windows only')

def video_acceptance():
 import signal,shutil
 old=json.loads((OUT/'owned-video.json').read_text());pid=old['pid']
 try:
  if b'latency-side-by-side.mp4' in Path(f'/proc/{pid}/cmdline').read_bytes():os.kill(pid,signal.SIGINT)
 except FileNotFoundError:pass
 time.sleep(.5)
 for filename in ['latency-side-by-side.mp4','latency-desktop-before.png']:
  if (OUT/filename).exists():shutil.move(OUT/filename,WORK/('calibration-private-'+filename))
 save('video-calibration-exclusion.json',{'reason':'Initial native preview included translucent desktop background; excluded from report artifacts. Calibration timing JSON remains unchanged. Acceptance video starts after setting both owned windows opaque.'})
 args=['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-framerate','30','-video_size','1920x1040','-i',os.environ['DISPLAY']+'+0,0']
 subprocess.run(args+['-frames:v','1',str(OUT/'latency-desktop-before.png')],check=True,timeout=10)
 log=(OUT/'video-acceptance-recorder.log').open('x');begin=time.time()*1000;p=subprocess.Popen(args+['-t','180','-c:v','libx264','-preset','superfast','-crf','30','-pix_fmt','yuv420p',str(OUT/'latency-side-by-side.mp4')],stdout=log,stderr=subprocess.STDOUT,start_new_session=True);save('owned-video-acceptance.json',{'pid':p.pid,'started_before_ms':begin,'started_after_ms':time.time()*1000,'crop':'1920x1040+0,0','fps':30,'limit_s':180});print('Acceptance video ready',p.pid)

def backend_readme_update():
 target=ROOT.parent/'backend/README.md';base=WORK/'backend-fix/README.md'
 assert target.read_bytes()==base.read_bytes(),'README independently changed; refusing overwrite'
 addition="""

## TASK-010 — sửa đồng bộ session sau restart/reconnect

Actor đồng bộ connected/session ngay sau khi lấy job khỏi queue, trước khi xử lý event. Điều này tránh loại nhầm availability ONLINE retained vừa tới trong lúc chờ queue và để node kẹt UNCONFIRMED_BOOT sau restart backend. Vẫn cần telemetry mới đúng session/boot để mở khóa; event session cũ không được phục hồi node. Không đổi MQTT/HTTP API hoặc schema SQLite.

Bộ hồi quy hiện72 Pytest và Ruff PASS, gồm4 trường hợp actor wake-up/session mới/cũ. Lỗi có2 ca tái hiện FAIL trước sửa và được xác minh phục hồi live cùng boot sau sửa. TASK-010 đã bổ sung UI REJECTED/TIMEOUT, pending/phiên mở qua restart, broker outage/reconnect/no-replay/AUTO offline và10 mẫu sensor → dashboard; xem hồ sơ completion trong firmware/docs/reports/evidence/task-010 và techs/backend.md. Môi trường QA dùng DB riêng/API8001, không thay cổng mặc định8000 hoặc dữ liệu người dùng.
"""
 target.write_bytes(target.read_bytes()+addition.encode());print('Updated backend README on task branch; runtime defaults unchanged')
if __name__=='__main__':
 command=sys.argv[1] if len(sys.argv)>1 else ''
 if command=='preflight':preflight()
 elif command=='infra-up':infra_up()
 elif command=='cli-probe':cli_probe()
 elif command=='web-up':web_up()
 elif command=='vscode-up':vscode_up()
 elif command=='vscode-isolate':vscode_isolate()
 elif command=='controller-restart':controller_restart()
 elif command=='serial-up':serial_up()
 elif command=='service-control-up':service_control_up()
 elif command=='backend-fix-publish':backend_fix_publish()
 elif command=='latency-up':latency_up()
 elif command=='latency-retry':latency_retry()
 elif command=='video-up':video_up()
 elif command=='opaque-windows':opaque_windows()
 elif command=='video-acceptance':video_acceptance()
 elif command=='backend-readme-update':backend_readme_update()
 elif command=='state':print(json.dumps(request('/state')))
 else:raise SystemExit('Unknown task subcommand')
