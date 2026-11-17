"""Stop only TASK-010 processes whose identity matches the recorded ownership."""
from pathlib import Path
import json,os,signal,time,subprocess,socket
from urllib.request import Request,urlopen
S=json.loads(Path('/tmp/task010-completion/state.json').read_text());OUT=Path(S['evidence']);WORK=Path('/tmp/task010-completion');actions=[]
def post(port,path):
 try:
  with urlopen(Request(f'http://127.0.0.1:{port}{path}',data=b'{}',headers={'Content-Type':'application/json'}),timeout=8) as r:v=json.load(r)
  actions.append({'port':port,'path':path,'result':v})
 except Exception as e:actions.append({'port':port,'path':path,'note':type(e).__name__})
def terminate(pid,needle,signum=signal.SIGTERM):
 try:
  raw=Path(f'/proc/{pid}/cmdline').read_bytes()
  if not raw:actions.append({'pid':pid,'note':'already exited or zombie'});return
  if needle.encode() not in raw:raise RuntimeError('Identity mismatch; refusing to signal '+str(pid))
  os.kill(pid,signum);actions.append({'pid':pid,'signal':signum.name,'identity_guard':needle})
 except FileNotFoundError:actions.append({'pid':pid,'note':'already exited'})
# Finalize video before closing the two recorded windows.
video=json.loads((OUT/'owned-video-acceptance.json').read_text());terminate(video['pid'],'latency-side-by-side.mp4',signal.SIGINT);time.sleep(.5)
result=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration,size:stream=width,height,avg_frame_rate','-of','json',str(OUT/'latency-side-by-side.mp4')],capture_output=True,text=True,check=True);meta=json.loads(result.stdout);trials=[x for x in json.loads((OUT/'latency-trials.json').read_text()) if not x['pilot']];duration=float(meta['format']['duration'])*1000
meta['acceptance_capture_covers_actions_and_render']=min(x['action_host_interval_ms'][0] for x in trials)>video['started_after_ms'] and max(x['render']['host_ms'] for x in trials)<video['started_before_ms']+duration
meta['time_reference_note']='Video is visual corroboration at30fps; quantitative result uses calibrated trusted action/render event intervals.'
(OUT/'video-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');assert meta['acceptance_capture_covers_actions_and_render'],'Video coverage insufficient'
post(18767,'/stop')
for name in ['owned-latency-controller-v2.json','owned-latency-controller.json']:
 if (OUT/name).exists():terminate(json.loads((OUT/name).read_text())['pid'],'latency.cjs')
# Close the isolated VSCode profile; no user VSCode windows share this profile.
for name in ['owned-vscode-isolated.json','owned-vscode.json']:
 if (OUT/name).exists():terminate(json.loads((OUT/name).read_text())['pid'],str(WORK/'vscode-profile'))
(WORK/'stop-serial').write_text('TASK-010 completion cleanup\n');time.sleep(.7)
pid=json.loads((WORK/'current-backend.json').read_text())['pid'];raw=Path(f'/proc/{pid}/environ').read_bytes();assert ('SMARTLIGHT_DB='+str(WORK/'qa.db')).encode()+b'\0' in raw
terminate(pid,'uvicorn',signal.SIGINT)
terminate(json.loads((OUT/'owned-liveserver.json').read_text())['pid'],str(WORK/'live.cjs'))
post(18765,'/stop');post(18766,'/stop')
owned=json.loads((OUT/'owned-broker.json').read_text());name=owned['name'];label=subprocess.run(['docker','inspect','--format','{{index .Config.Labels "smartlight.qa"}}',name],capture_output=True,text=True,check=True).stdout.strip();assert label==OUT.name
subprocess.run(['docker','stop',name],capture_output=True,text=True,check=True);subprocess.run(['docker','rm',name],capture_output=True,text=True,check=True);actions.append({'container':name,'removed_owned_broker':True})
time.sleep(.7)
ports={}
for port in [1883,11883,11884,19011,8001,5500,4000,18765,18766,18767,19222]:
 s=socket.socket()
 try:s.bind(('127.0.0.1',port));ports[str(port)]='free'
 except OSError as e:ports[str(port)]='unavailable: '+str(e)
 finally:s.close()
result={'at_host_ms':time.time()*1000,'actions':actions,'ports':ports,'source_repos_and_existing_data':'Firmware/backend/dashboard source retained; QA DB remains in /tmp, no live DB deletion','result':'PASS' if all(x=='free' for x in ports.values()) else 'REVIEW'};(OUT/'cleanup.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'result':result['result'],'ports':ports,'video_covers_all10':meta['acceptance_capture_covers_actions_and_render'],'video_mb':round(int(meta['format']['size'])/1e6,2)},ensure_ascii=False))
