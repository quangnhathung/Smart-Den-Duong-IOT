// Real browser/UI/telemetry observation only; no data mocks or product patches.
const {chromium}=require('/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const fs=require('fs'),http=require('http'),cp=require('child_process'),crypto=require('crypto');
const state=JSON.parse(fs.readFileSync('/tmp/task010-completion/state.json','utf8')),out=state.evidence;
const stream=fs.createWriteStream(out+'/latency-events-v4.jsonl',{flags:'wx'}),now=()=>performance.timeOrigin+performance.now();
const records=[],trials=[];let active=null,ctx,page,wokwi,frame,server,browserServer;let serialNo=0;
function record(event,data={}){const v={host_ms:now(),event,...data};records.push(v);stream.write(JSON.stringify(v)+'\n');return v;}
async function json(url,data){const r=await fetch(url,{method:data===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});if(!r.ok)throw Error('HTTP '+r.status+' '+url);return r.json();}
async function calibrate(target){const a=[];for(let i=0;i<7;i++){const low=now(),remote=await target.evaluate(()=>performance.timeOrigin+performance.now()),high=now();a.push({low,remote,high,rtt:high-low,offsetLow:low-remote,offsetHigh:high-remote});}return a.sort((a,b)=>a.rtt-b.rtt)[0];}
async function setup(){
 wokwi=await chromium.connectOverCDP('http://127.0.0.1:19222');const wp=wokwi.contexts()[0].pages().find(p=>p.url().startsWith('vscode-file:'));frame=wp.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode'));if(!frame)throw Error('Wokwi frame missing');
 browserServer=await chromium.launchServer({headless:false,channel:'chrome',args:['--window-position=960,0','--window-size=960,1040']});const browser=await chromium.connect(browserServer.wsEndpoint());ctx=await browser.newContext({viewport:null});page=await ctx.newPage();
 fs.writeFileSync(out+'/owned-latency-browser.json',JSON.stringify({pid:process.pid,chrome_pid:browserServer.process().pid},null,2));
 await page.exposeBinding('qaDOM',(_source,v)=>record(v.event,{...v,trial:active?.id??null}));
 page.on('response',async response=>{if(!response.url().endsWith('/api/nodes'))return;try{const v=(await response.json()).find(n=>n.node_id==='node_01');record('api_sample',{node:v,trial:active?.id??null});}catch{}});
 page.on('pageerror',error=>record('dashboard_pageerror',{message:error.message}));
 await page.goto('http://127.0.0.1:5500/#nodes/node_01');await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
 await page.evaluate(()=>{
  window.__qaPageId=crypto.randomUUID();const emit=(event,v={})=>window.qaDOM({event,page_id:window.__qaPageId,browser_ms:performance.timeOrigin+performance.now(),visibility:document.visibilityState,...v});
  document.addEventListener('visibilitychange',()=>emit('dashboard_visibility'));emit('dashboard_visibility');
  const panel=document.getElementById('detailReadings');let seen='';
  const read=()=>Object.fromEntries(Array.from(panel.querySelectorAll('.reading')).map(e=>[e.querySelector('dt').textContent,e.querySelector('dd').textContent]));
  new MutationObserver(()=>{const first=read(),key=first['Boot / sequence'];if(!key||key===seen)return;seen=key;requestAnimationFrame(()=>requestAnimationFrame(()=>{const values=read();if(values['Boot / sequence']!==key)return;const row=Array.from(panel.querySelectorAll('.reading')).find(e=>e.querySelector('dt').textContent==='LDR · ADC raw'),rect=row.getBoundingClientRect();emit('dom_render',{key,readings:values,ldr_visible:rect.top>=0&&rect.bottom<=innerHeight});}));}).observe(panel,{childList:true,subtree:true});
  const label=document.createElement('p');label.textContent='ĐO LIVE TASK-010 · WOKWI/MQTT/API THẬT';label.style.cssText='background:#fef3c7;font:600 12px system-ui;padding:6px';document.getElementById('main').prepend(label);
  Array.from(panel.querySelectorAll('.reading')).find(e=>e.querySelector('dt').textContent==='LDR · ADC raw').scrollIntoView({block:'center'});
 });
 await frame.evaluate(()=>{window.__qaPageId??=crypto.randomUUID();window.__qaVisibility=[];const take=()=>window.__qaVisibility.push({browser_ms:performance.timeOrigin+performance.now(),visibility:document.visibilityState});document.addEventListener('visibilitychange',take);take();});
 // Both windows belong to this QA run; preserve process ownership in the video metadata.
 const previous=JSON.parse(fs.readFileSync(out+'/video-windows.json','utf8'));const x=(...a)=>cp.execFileSync('xdotool',a.map(String),{encoding:'utf8',timeout:5000}).trim();
 const old=previous.find(w=>w.name==='wokwi');let win;
 for(const id of x('search','--pid',browserServer.process().pid).split('\n')){try{if(x('getwindowname',id).includes('SmartLight')){win=id;break;}}catch{}}
 if(!win)throw Error('Owned Chrome window missing');
 for(const [id,left] of [[old.window_id,0],[win,960]]){cp.spawnSync('bspc',['node','0x'+Number(id).toString(16),'-g','hidden=off']);cp.spawnSync('bspc',['node','0x'+Number(id).toString(16),'-d','focused']);cp.spawnSync('bspc',['node','0x'+Number(id).toString(16),'-t','floating']);x('windowsize',id,960,1040);x('windowmove',id,left,0);x('windowraise',id);}
 fs.writeFileSync(out+'/latency-video-windows.json',JSON.stringify([{name:'wokwi',id:old.window_id},{name:'dashboard',id:win,chrome_pid:browserServer.process().pid}],null,2));
 record('setup_complete',{dashboard_url:page.url(),wokwi_url:frame.url(),method:'Native LDR Home/End keys in VSCode Wokwi; real dashboard at actual viewport; no iframe dashboard or fixture'});
}
async function trial(pilot,key,delayMs){
 const id=pilot?'pilot-'+(++serialNo):'sample-'+(trials.filter(t=>!t.pilot).length+1);active={id};await new Promise(r=>setTimeout(r,delayMs));
 const node=(await json('http://127.0.0.1:8001/api/nodes'))[0],baseline=node.telemetry;
 const before=await frame.getByRole('slider').first().getAttribute('aria-valuetext');const expectedHigh=key==='Home';
 if(!baseline||node.freshness!=='FRESH'||expectedHigh&&baseline.ldr_adc>3900||!expectedHigh&&baseline.ldr_adc<100)throw Error('Baseline not ready/opposite for '+id);
 const sensorClock=await calibrate(frame),renderClock=await calibrate(page);const startHost=now();
 await frame.evaluate(()=>{window.__qaAction=null;const input=document.querySelector('input[type=range]');if(!input)throw Error('LDR control missing');input.addEventListener('keydown',e=>{window.__qaAction={browser_ms:performance.timeOrigin+e.timeStamp,page_id:window.__qaPageId,key:e.key,trusted:e.isTrusted,visibility:document.visibilityState};},{once:true,capture:true});});
 await frame.getByRole('slider').first().press(key);const action=await frame.evaluate(()=>window.__qaAction),after=await frame.getByRole('slider').first().getAttribute('aria-valuetext');record('sensor_action',{trial:id,key,before,after,baseline,action});
 let render,api;const deadline=now()+8000;
 while(now()<deadline){
  render=records.find(e=>e.event==='dom_render'&&e.trial===id&&e.host_ms>=startHost&&e.key.startsWith(baseline.boot_id+' / ')&&BigInt(e.key.split('/')[1].trim())>BigInt(baseline.seq)&&(expectedHigh?Number(e.readings['LDR · ADC raw'].replace(/[^0-9]/g,''))>3900:Number(e.readings['LDR · ADC raw'].replace(/[^0-9]/g,''))<100));
  if(render){api=records.find(e=>e.event==='api_sample'&&e.node?.telemetry&&e.node.telemetry.boot_id+' / '+e.node.telemetry.seq===render.key);if(api)break;}
  await new Promise(r=>setTimeout(r,30));
 }
 const sensorClockAfter=await calibrate(frame),renderClockAfter=await calibrate(page);const visibility=await frame.evaluate(()=>window.__qaVisibility);const reasons=[];
 const actionLow=action?.browser_ms+Math.min(sensorClock.offsetLow,sensorClockAfter.offsetLow),actionHigh=action?.browser_ms+Math.max(sensorClock.offsetHigh,sensorClockAfter.offsetHigh);
 let interval=null,status='INCOMPLETE';
 if(!action||!action.trusted)reasons.push('Missing trusted LDR keydown');
 if(action?.visibility!=='visible')reasons.push('Wokwi hidden at action');
 if(!render||!api)reasons.push('Missing matching real API sample and DOM render');
 if(render){
  if(render.visibility!=='visible'||!render.ldr_visible)reasons.push('LDR raw not visibly rendered');
  if(records.some(e=>e.event==='dashboard_visibility'&&e.visibility==='hidden'&&e.host_ms>=startHost&&e.host_ms<=render.host_ms))reasons.push('Dashboard hidden during trial');
  if(visibility.some(e=>e.visibility==='hidden'&&e.browser_ms>=action.browser_ms&&e.browser_ms<=action.browser_ms+9000))reasons.push('Wokwi hidden during trial');
  if(api&&Date.parse(api.node.last_seen)<actionHigh)reasons.push('API sample predates action bounds');
  const rLow=render.browser_ms+Math.min(renderClock.offsetLow,renderClockAfter.offsetLow),rHigh=render.browser_ms+Math.max(renderClock.offsetHigh,renderClockAfter.offsetHigh);interval=[rLow-actionHigh,rHigh-actionLow];
  if(!reasons.length)status=interval[0]>=0&&interval[1]<=3000?'PASS':interval[0]>3000?'FAIL':'INCOMPLETE';
 }
 const row={id,pilot,key,before,after,baseline,action,action_host_interval_ms:[actionLow,actionHigh],sensorClock,sensorClockAfter,renderClock,renderClockAfter,render,api,latency_interval_ms:interval,status,reasons};trials.push(row);record('trial_summary',{trial:id,status,latency_interval_ms:interval,reasons});fs.writeFileSync(out+'/latency-trials.json',JSON.stringify(trials,null,2));active=null;return row;
}
async function stop(){try{await ctx.close();await browserServer.close();}finally{stream.end();server.close();}}
(async()=>{await setup();server=http.createServer(async(req,res)=>{try{let raw='';for await(const part of req)raw+=part;const input=raw?JSON.parse(raw):{};let result;if(req.url==='/trial')result=await trial(!!input.pilot,input.key,input.delay_ms??500);else if(req.url==='/state')result={trials:trials.map(t=>({id:t.id,status:t.status,latency:t.latency_interval_ms,reasons:t.reasons})),dashboard:await page.evaluate(()=>({visible:document.visibilityState,inner:[innerWidth,innerHeight]})),wokwi:await frame.evaluate(()=>({visible:document.visibilityState}))};else if(req.url==='/stop'){res.writeHead(200);res.end('{}');await stop();return;}else throw Error('Unknown QA path');res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));}catch(e){record('error',{message:e.message});res.writeHead(500);res.end(JSON.stringify({error:e.message}));}}).listen(18767,'127.0.0.1');console.log('Latency controller ready 18767');})().catch(e=>{console.error(e);process.exitCode=1;});
