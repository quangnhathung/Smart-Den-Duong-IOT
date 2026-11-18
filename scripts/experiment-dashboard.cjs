// TASK-012 observer/video controller for an owned QA Chrome, never the user's browser.
const {chromium}=require(process.env.SMARTLIGHT_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),http=require('node:http'),path=require('node:path');
const cfg=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));const log=fs.createWriteStream(path.join(cfg.qa,'dashboard-events.jsonl'),{flags:'a'});
let browser,context,page,videoContext;const errors=[];
function record(event,data){log.write(JSON.stringify({event,host_ms:Date.now(),monotonic_ns:process.hrtime.bigint().toString(),...data})+'\n');}
function watch(p){p.on('pageerror',e=>{errors.push(e.message);record('pageerror',{message:e.message});});p.on('response',async r=>{if(r.url().endsWith('/api/nodes'))try{record('nodes',{status:r.status(),value:await r.json()});}catch{}});}
(async()=>{
 const server=await chromium.launchServer({channel:'chrome',headless:false,args:['--window-position=0,0','--window-size=1280,1000','--disable-background-timer-throttling','--disable-renderer-backgrounding']});
 browser=await chromium.connect(server.wsEndpoint());context=await browser.newContext({viewport:{width:1280,height:900}});page=await context.newPage();watch(page);await page.goto('http://127.0.0.1:5500/#overview');
 fs.writeFileSync(path.join(cfg.qa,'owned-dashboard.json'),JSON.stringify({controller_pid:process.pid,chrome_pid:server.process().pid,ws_endpoint:server.wsEndpoint()},null,2)+'\n');
 const api=http.createServer(async(req,res)=>{try{let raw='';for await(const c of req)raw+=c;const v=raw?JSON.parse(raw):{};let result;
 if(req.url==='/state')result={url:page.url(),text:await page.locator('body').innerText(),errors,visibility:await page.evaluate(()=>document.visibilityState)};
 else if(req.url==='/goto'){await page.goto('http://127.0.0.1:5500/'+(v.hash||'#overview'));result={url:page.url()};}
 else if(req.url==='/shot'){const p=path.join(cfg.qa,'screenshots',path.basename(v.name));fs.mkdirSync(path.dirname(p),{recursive:true});await page.screenshot({path:p,fullPage:true});result={path:p};}
 else if(req.url==='/video/start'){if(videoContext)throw Error('Video already recording');videoContext=await browser.newContext({viewport:{width:1920,height:1080},recordVideo:{dir:path.join(cfg.qa,'video-raw'),size:{width:1920,height:1080}}});page=await videoContext.newPage();watch(page);await page.goto('http://127.0.0.1:5500/#overview');result={recording:true};}
 else if(req.url==='/video/stop'){if(!videoContext)throw Error('No video');const video=page.video();await videoContext.close();result={path:await video.path()};videoContext=null;page=context.pages()[0];}
 else if(req.url==='/snapshot')result={inputs:await page.locator('input,select,button').evaluateAll(es=>es.map(e=>({tag:e.tagName,id:e.id,type:e.type,text:e.textContent,label:e.getAttribute('aria-label'),value:e.value}))),text:await page.locator('body').innerText()};
 else throw Error('Unknown request');res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));
 }catch(e){record('error',{error:e.message});res.writeHead(500,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}});
 api.listen(18773,'127.0.0.1',()=>console.log('QA dashboard ready18773'));
 process.on('SIGTERM',()=>{api.close();browser.close().finally(()=>{log.end();server.close().finally(()=>process.exit(0));});});
})().catch(e=>{console.error(e);process.exit(1)});
