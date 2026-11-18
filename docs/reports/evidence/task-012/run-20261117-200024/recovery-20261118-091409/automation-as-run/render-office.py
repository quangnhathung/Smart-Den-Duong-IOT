"""WPS native page/slide PNG proof; never exports PDF or edits the source."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,signal,sys,time
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('output',type=Path);args=parser.parse_args();source=args.source.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
from pywpsrpc.common import QtApp,S_OK
qt=QtApp(sys.argv);os.environ['LD_LIBRARY_PATH']='/usr/lib/office6'
preexisting=set()
for process in Path('/proc').iterdir():
 if not process.name.isdigit():continue
 try:
  cmd=(process/'cmdline').read_bytes().split(b'\0')[0].decode(errors='replace')
  if Path(cmd).name in ['wps','wpp','wpsoffice','et','wpspdf']:preexisting.add(int(process.name))
 except OSError:pass
writer=source.suffix.lower()=='.docx'
if writer:
 from pywpsrpc.rpcwpsapi import createWpsRpcInstance,wpsapi
 hr,rpc=createWpsRpcInstance()
else:
 from pywpsrpc.rpcwppapi import createWppRpcInstance,wppapi
 hr,rpc=createWppRpcInstance()
assert hr==S_OK,hr
rpc.setProcessPath('/usr/lib/office6/wps' if writer else '/usr/lib/office6/wpp');rpc.setProcessArgs(['-multiply']);rpc.setStartTimeout(30000000)
hr,app=rpc.getWpsApplication() if writer else rpc.getWppApplication();assert hr==S_OK,hr
hr,pid=rpc.getProcessPid();assert hr==S_OK,hr
assert pid not in preexisting,('RPC returned a preexisting application; will not control or close it',pid)
proc=Path('/proc')/str(pid);ticks=(proc/'stat').read_text().split()[21]
meta=dict(host_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),at=datetime.datetime.now().astimezone().isoformat(timespec='seconds'),source=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),owned_pid=pid,start_ticks=ticks,status='OPENING',images=[],preexisting_wps_pids=sorted(preexisting),helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def save():
 (out/'proof.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
save();docs=app.Documents if writer else app.Presentations;assert docs.Count==0,'Fresh QA instance already has documents';doc=None
try:
 if writer:
  hr,doc=docs.Open(str(source),ReadOnly=True,AddToRecentFiles=False);assert hr==S_OK,hr
  app.Visible=False;hr,count=doc.ComputeStatistics(wpsapi.wdStatisticPages);assert hr==S_OK,hr
  pages=doc.ActiveWindow.ActivePane.Pages
 else:
  hr,doc=docs.Open(str(source),ReadOnly=wppapi.MsoTriState.msoTrue,WithWindow=wppapi.MsoTriState.msoFalse);assert hr==S_OK,hr
  count=doc.Slides.Count;pages=doc.Slides
 meta['count']=count
 for i in range(1,count+1):
  hr,page=pages.Item(i);assert hr==S_OK,hr
  target=out/f'{"page" if writer else "slide"}-{i:02}.png'
  hr=page.SaveAsPNG(str(target)) if writer else page.Export(str(target),'PNG',1920,1080)
  assert hr==S_OK and target.exists() and target.stat().st_size>1000,(i,hr)
  meta['images'].append(dict(index=i,path=target.name,bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest()));save();print('RENDERED',i,flush=True)
 meta['status']='RENDERED_IMAGES';meta['source_unchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==meta['sha256'];assert meta['source_unchanged']
except Exception as exc:
 meta['status']='INCOMPLETE';meta['error']=repr(exc)
finally:
 if doc is not None:
  doc.Close(wpsapi.wdDoNotSaveChanges) if writer else doc.Close()
 meta['remaining_documents']=docs.Count
 if docs.Count==0:
  app.Quit(wpsapi.wdDoNotSaveChanges) if writer else app.Quit();meta['quit_requested']=True
  for _ in range(20):
   if not proc.exists() or (proc/'stat').read_text().split()[2]=='Z':break
   time.sleep(.1)
  if proc.exists() and (proc/'stat').read_text().split()[21]==ticks and (proc/'stat').read_text().split()[2]!='Z':
   os.kill(pid,signal.SIGTERM);meta['owned_empty_instance_terminated']=True
   for _ in range(100):
    if not proc.exists() or (proc/'stat').read_text().split()[2]=='Z':break
    time.sleep(.1)
  meta['process_stopped']=not proc.exists() or (proc/'stat').read_text().split()[2]=='Z'
 save();print(json.dumps({k:meta.get(k) for k in ['status','count','source_unchanged','process_stopped']}),flush=True)
 # pywpsrpc/Qt wrappers crash during destructor teardown on this WPS build.
 # All files are flushed and only the newly created empty instance is stopped.
 os._exit(0 if meta['status']=='RENDERED_IMAGES' else 1)
