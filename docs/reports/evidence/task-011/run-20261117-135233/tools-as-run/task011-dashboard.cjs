const {chromium}=require('/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const fs=require('fs'),http=require('http'),cp=require('child_process');
const S=JSON.parse(fs.readFileSync('/tmp/task011-active.json','utf8')),OUT=S.evidence,QA=S.qa;
const now=()=>performance.timeOrigin+performance.now(),records=[],trials=fs.existsSync(OUT+'/latency-trials.json')?JSON.parse(fs.readFileSync(OUT+'/latency-trials.json','utf8')):[];let page,server,active=null,currentNode=null;const frames=[];
const stream=fs.createWriteStream(OUT+'/ui-events.jsonl',{flags:'a'});
function record(event,data={}){const e={event,host_ms:now(),monotonic_ms:performance.now(),...data};records.push(e);stream.write(JSON.stringify(e)+'\n');return e;}
async function api(path,body){const r=await fetch('http://127.0.0.1:8001'+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});if(!r.ok)throw Error('API '+r.status+':'+await r.text());return r.json();}
async function calibrate(target){let best;for(let i=0;i<5;i++){const low=now(),remote=await target.evaluate(()=>performance.timeOrigin+performance.now()),high=now();const v={low,remote,high,offsetLow:low-remote,offsetHigh:high-remote};if(!best||high-low<best.high-best.low)best=v;}return best;}
async function go(node){
 currentNode=node;await page.goto('http://127.0.0.1:5500/#nodes/'+node);await page.waitForFunction(()=>document.querySelector('#detailReadings .reading'));
 await page.evaluate(()=>{
 const panel=document.getElementById('detailReadings');let seen='';const read=()=>Object.fromEntries(Array.from(panel.querySelectorAll('.reading')).map(e=>[e.querySelector('dt').textContent,e.querySelector('dd').textContent]));
 new MutationObserver(()=>{const v=read(),key=v['Boot / sequence'];if(!key||key===seen)return;seen=key;requestAnimationFrame(()=>requestAnimationFrame(()=>{const readings=read();if(readings['Boot / sequence']!==key)return;const e=Array.from(panel.querySelectorAll('.reading')).find(e=>e.querySelector('dt').textContent==='LDR · ADC raw'),r=e.getBoundingClientRect();window.qaDOM({browser_ms:performance.timeOrigin+performance.now(),visibility:document.visibilityState,readings,ldr_visible:r.top>=0&&r.bottom<=innerHeight});}));}).observe(panel,{childList:true,subtree:true});
 Array.from(panel.querySelectorAll('.reading')).find(e=>e.querySelector('dt').textContent==='LDR · ADC raw').scrollIntoView({block:'center'});
 });
 return {url:page.url(),text:(await page.locator('body').innerText()).slice(-4500)};
}
async function trial(node,key,pilot=false){
 if(currentNode!==node)await go(node);const f=frames[Number(node.slice(-1))-1];
 const baseline=(await api('/api/nodes')).find(n=>n.node_id===node);if(baseline.freshness!=='FRESH')throw Error('Baseline stale');
 const high=key==='Home';if(high&&baseline.telemetry.ldr_adc>3900||!high&&baseline.telemetry.ldr_adc<100)throw Error('Baseline already at target');
 const id=node+'-'+(pilot?'pilot':'sample')+'-'+(trials.length+1);active=id;
 await page.locator('#detailReadings').getByText('LDR · ADC raw',{exact:true}).scrollIntoViewIfNeeded();
 const sensorClock=await calibrate(f),renderClock=await calibrate(page);await new Promise(r=>setTimeout(r,750));const startHost=now();
 await f.evaluate(()=>{window.__qaAction=null;const input=document.querySelector('input[aria-valuetext$="lux"]');if(!input)throw Error('LDR slider missing');input.addEventListener('keydown',e=>window.__qaAction={browser_ms:performance.timeOrigin+e.timeStamp,key:e.key,trusted:e.isTrusted,visibility:document.visibilityState},{once:true,capture:true});});
 const slider=f.locator('input[aria-valuetext$="lux"]'),sliderBefore=await slider.getAttribute('aria-valuetext');
 const beforeLux=Number(sliderBefore.replace(/[^0-9.]/g,''));if(high&&beforeLux<=0.1||!high&&beforeLux>=100000)throw Error('Slider already at requested target before action');
 await slider.press(key);const sliderAfter=await slider.getAttribute('aria-valuetext');const action=await f.evaluate(()=>window.__qaAction);record('sensor_action',{node,id,key,action,baseline,sliderBefore,sliderAfter});
 let render,matched;const deadline=now()+8000;
 while(now()<deadline){render=records.find(e=>e.event==='dom_render'&&e.trial===id&&e.host_ms>=startHost&&e.readings['Boot / sequence']?.startsWith(baseline.telemetry.boot_id+' / ')&&BigInt(e.readings['Boot / sequence'].split('/')[1].trim())>BigInt(baseline.telemetry.seq)&&(high?Number(e.readings['LDR · ADC raw'].replace(/[^0-9]/g,''))>3900:Number(e.readings['LDR · ADC raw'].replace(/[^0-9]/g,''))<100));if(render){matched=records.find(e=>e.event==='api_sample'&&e.node?.telemetry&&e.node.telemetry.boot_id+' / '+e.node.telemetry.seq===render.readings['Boot / sequence']);if(matched)break;}await new Promise(r=>setTimeout(r,30));}
 const sensorAfter=await calibrate(f),renderAfter=await calibrate(page),reasons=[];
 const aLow=action?.browser_ms+Math.min(sensorClock.offsetLow,sensorAfter.offsetLow),aHigh=action?.browser_ms+Math.max(sensorClock.offsetHigh,sensorAfter.offsetHigh);
 let bounds=null,status='INCOMPLETE';
 if(Number(sliderAfter.replace(/[^0-9.]/g,''))!==(high?0.1:100000))reasons.push('Slider did not reach requested value');
 if(!action?.trusted||action.visibility!=='visible')reasons.push('Missing trusted visible action');
 if(!render||!matched)reasons.push('Missing matched API/DOM');
 if(render){if(render.visibility!=='visible'||!render.ldr_visible)reasons.push('Dashboard reading hidden');if(matched&&Date.parse(matched.node.last_seen)<aHigh)reasons.push('API precedes action');bounds=[render.browser_ms+Math.min(renderClock.offsetLow,renderAfter.offsetLow)-aHigh,render.browser_ms+Math.max(renderClock.offsetHigh,renderAfter.offsetHigh)-aLow];if(!reasons.length)status=bounds[0]>=0&&bounds[1]<=3000?'PASS':bounds[0]>3000?'FAIL':'INCOMPLETE';}
 const row={runtime:'sensor-coalescing-fixed-cpu4',slider_before:sliderBefore,slider_after:sliderAfter,id,node,key,pilot,status,reasons,latency_interval_ms:bounds,baseline,action,sensorClock,sensorAfter,renderClock,renderAfter,render,api:matched};trials.push(row);fs.writeFileSync(OUT+'/latency-trials.json',JSON.stringify(trials,null,2));record('trial_summary',{id,node,pilot,status,reasons,bounds});active=null;return {id,node,status,reasons,bounds};
}
(async()=>{
 for(let n=1;n<=3;n++){const b=await chromium.connectOverCDP('http://127.0.0.1:'+(19221+n));const p=b.contexts()[0].pages().find(p=>p.url().startsWith('vscode-file:'));let f;for(let i=0;i<40;i++){f=p.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode'));if(f)break;await new Promise(r=>setTimeout(r,250));}if(!f)throw Error('Simulator missing '+n);frames.push(f);}
 server=await chromium.launchServer({headless:false,channel:'chrome',args:['--remote-debugging-port=19225','--window-position=960,0','--window-size=960,1040']});
 fs.writeFileSync(OUT+'/owned-dashboard-browser.json',JSON.stringify({controller_pid:process.pid,chrome_pid:server.process().pid},null,2));
 const browser=await chromium.connect(server.wsEndpoint());const context=await browser.newContext({viewport:null});page=await context.newPage();await page.exposeBinding('qaDOM',(_,v)=>record('dom_render',{...v,node:currentNode,trial:active}));
 page.on('response',async r=>{if(!r.url().endsWith('/api/nodes'))return;try{for(const node of await r.json())record('api_sample',{node,trial:active});}catch{}});page.on('pageerror',e=>record('pageerror',{message:e.message}));
 await page.goto('http://127.0.0.1:5500/#overview');
 http.createServer(async(req,res)=>{try{let raw='';for await(const x of req)raw+=x;const v=raw?JSON.parse(raw):{};let result;
 if(req.url==='/state')result={url:page.url(),text:(await page.locator('body').innerText()).slice(-7000),visible:await page.evaluate(()=>document.visibilityState),trials:trials.map(t=>({id:t.id,status:t.status,bounds:t.latency_interval_ms}))};
 else if(req.url==='/go')result=await go(v.node);
 else if(req.url==='/trial')result=await trial(v.node,v.key,!!v.pilot);
 else if(req.url==='/overview'){currentNode=null;await page.goto('http://127.0.0.1:5500/#overview');result={ok:true};}
 else if(req.url==='/shot'){await page.screenshot({path:QA+'/output/playwright/'+v.name+'.png'});result={ok:true};}
 else throw Error('Unknown request');res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));
 }catch(e){record('error',{message:e.message});res.writeHead(500);res.end(JSON.stringify({error:e.message}));}}).listen(18773,'127.0.0.1',()=>console.log('Dashboard controller ready18773'));
})().catch(e=>{console.error(e);process.exit(1)});
