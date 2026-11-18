// TASK-012 QA bridge: real Playwright UI actions, no firmware or sensor injection.
const {chromium} = require(process.env.SMARTLIGHT_PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');
const stateFile = process.argv[2];
if (!stateFile) throw Error('Usage: node scripts/experiment-ui.cjs RUN/runtime.json');
const cfg = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
const sessions = [];
const appliedValues = new WeakMap();
const viewportSizes = new WeakMap();
const locks = [Promise.resolve(), Promise.resolve(), Promise.resolve()];
const log = fs.createWriteStream(path.join(cfg.qa, 'ui-events.jsonl'), {flags:'a'});
function record(event, data) { log.write(JSON.stringify({event, host_ms:Date.now(), monotonic_ns:process.hrtime.bigint().toString(), ...data})+'\n'); }
function sim(page) { const f=page.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode')); if(!f)throw Error('Simulator frame missing');return f; }
async function command(page,label) {
 await page.keyboard.press('Escape'); await page.locator('body').evaluate(b=>{b.tabIndex=-1;b.focus();});
 await page.keyboard.press('F1'); await page.waitForFunction(()=>document.activeElement?.tagName==='INPUT',null,{timeout:7000});
 await page.keyboard.type(label); await page.getByText(label,{exact:true}).first().waitFor({state:'visible',timeout:7000}); await page.keyboard.press('Enter');
}
async function inspect(page) {
 const f=sim(page);return {text:await f.locator('body').innerText(),parts:await f.locator('body').evaluate(b=>Array.from(b.querySelectorAll('*')).filter(e=>e.tagName.toLowerCase().startsWith('wokwi-')).map(e=>({tag:e.tagName,id:e.id}))),inputs:await f.locator('input').evaluateAll(es=>es.map(e=>({outer:e.outerHTML,value:e.value}))),buttons:await f.getByRole('button').allTextContents()};
}
async function pointerClick(locator, options={}, measuredBox=null) {
 // Send real pointer input to the measured viewport point. Avoid repeated
 // locator actionability/scroll round trips across the Electron CDP bridge.
 const box=measuredBox||await locator.boundingBox();if(!box||box.width<=0||box.height<=0)throw Error('QA pointer target is not visible');
 const page=locator.page();let viewport=viewportSizes.get(page);
 if(!viewport){viewport=await page.evaluate(()=>({width:innerWidth,height:innerHeight}));viewportSizes.set(page,viewport);}
 const point={x:box.x+(options.position?.x??box.width/2),y:box.y+(options.position?.y??box.height/2)};
 if(point.x<0||point.y<0||point.x>=viewport.width||point.y>=viewport.height)throw Error('QA pointer target is outside the viewport');
 await page.mouse.click(point.x,point.y);
}
async function dismiss(f) {const button=f.locator('[class*="diagram-editor_selectedPartInfo"] button').last();if(await button.count())await pointerClick(button);}
async function selectPart(page,part) {const f=sim(page);await dismiss(f);await f.locator(part).click();return inspect(page);}
async function setRange(sl,value) {
 const started=Date.now();let afterClick;
 const info=await sl.evaluate(e=>({min:Number(e.min),max:Number(e.max),step:Number(e.step||1),value:Number(e.value),clipped:!!e.style.clip}));
 const target=info.clipped?sl.locator('xpath=ancestor::span[contains(@class,"MuiSlider-root")][1]'):sl;const box=await target.boundingBox();if(!box)throw Error('Slider not visible');
 const padding=info.clipped?0:8;
 await pointerClick(target,{position:{x:Math.max(1,Math.min(box.width-1,padding+(box.width-2*padding)*(value-info.min)/(info.max-info.min))),y:box.height/2}},box);
 for(let i=0;i<16;i++){const current=Number(await sl.inputValue());if(i===0)afterClick=current;if(Math.abs(current-value)<1e-8){record('range',{value,initial:info.value,after_click:afterClick,correction_keys:i,started_ms:started,finished_ms:Date.now()});return;}await sl.press(current<value?'ArrowRight':'ArrowLeft');}
 throw Error('Slider value not reached: '+await sl.inputValue()+' wanted '+value);
}
async function operate(page,v) {
 if(v.kind==='start') {await command(page,'Wokwi: Start Simulator');return {started:true};}
 if(v.kind==='stop') {await command(page,'Wokwi: Stop Simulator');return {stopped:true};}
 if(v.kind==='inspect') return inspect(page);
 if(v.kind==='reset-cache') {appliedValues.delete(page);viewportSizes.delete(page);return {cache_reset:true,no_sensor_change:true};}
 if(v.kind==='fit') {const viewer=sim(page).locator('[class*="diagram-editor_viewer"]').first();await viewer.evaluate(e=>{e.tabIndex=-1;e.focus();});await viewer.press('f');return {fit:true};}
 if(v.kind==='part')return selectPart(page,v.part);
 if(v.kind==='prepare-scene') {
  const f=sim(page),last=appliedValues.get(page)||{};
  if(v.lux!==undefined&&v.lux!==last.lux&&!await f.locator('input[aria-valuetext$="lux"]').count()){await dismiss(f);await pointerClick(f.locator('wokwi-photoresistor-sensor'));}
  else if(v.distance!==undefined&&v.distance!==last.distance&&!await f.locator('input[min="2"][max="400"]').count()){await dismiss(f);await pointerClick(f.locator('wokwi-hc-sr04'));}
  return {prepared:true,no_sensor_change:true};
 }
 if(v.kind==='key') {await sim(page).locator(v.selector||'input[role=slider]').nth(v.index||0).press(v.key);return inspect(page);}
 if(v.kind==='fill') {await sim(page).locator(v.selector).fill(String(v.value));if(v.enter)await sim(page).locator(v.selector).press('Enter');return inspect(page);}
 if(v.kind==='arm-motion') {const f=sim(page);if(!await f.getByRole('button',{name:/^Simulate motion$/i}).count()){await dismiss(f);await f.locator('wokwi-pir-motion-sensor').click();}return {armed:true};}
 if(v.kind==='motion') {const f=sim(page);if(!await f.getByRole('button',{name:/^Simulate motion$/i}).count()){await dismiss(f);await f.locator('wokwi-pir-motion-sensor').click();}await f.getByRole('button',{name:/^Simulate motion$/i}).click();return {motion_clicked:true,applied_host_ms:Date.now()};}
 if(v.kind==='shot') {const name=path.basename(v.name);const dest=path.join(cfg.qa,'screenshots',name);fs.mkdirSync(path.dirname(dest),{recursive:true});await page.screenshot({path:dest});return {path:dest};}
 if(v.kind==='scene') {
  const f=sim(page),last=appliedValues.get(page)||{},effects=[];
  if(v.lux!==undefined&&v.lux!==last.lux){if(!await f.locator('input[aria-valuetext$="lux"]').count()){await dismiss(f);await pointerClick(f.locator('wokwi-photoresistor-sensor'));}const sl=f.locator('input[aria-valuetext$="lux"]');if(v.lux===0.1)await sl.press('Home');else if(v.lux===100000)await sl.press('End');else {await setRange(sl,Math.log10(v.lux));}last.lux=v.lux;effects.push({kind:'lux',value:v.lux,host_ms:Date.now()});}
  if(v.distance!==undefined&&v.distance!==last.distance){if(!await f.locator('input[min="2"][max="400"]').count()){await dismiss(f);await pointerClick(f.locator('wokwi-hc-sr04'));}await setRange(f.locator('input[min="2"][max="400"]'),v.distance);last.distance=v.distance;effects.push({kind:'distance',value:v.distance,host_ms:Date.now()});}
  if(v.current!==undefined&&v.current!==last.current){const sl=f.locator('input[max="1023"]');const unchanged=Number(await sl.inputValue())===v.current;if(!unchanged)await sl.press(v.current===0?'Home':'End');last.current=v.current;effects.push({kind:'current',value:v.current,unchanged,host_ms:Date.now()});}
  appliedValues.set(page,last);return {scene_applied:true,effects};
 }
 throw Error('Unknown UI operation');
}
(async()=>{
 for(let n=1;n<=3;n++) {const browser=await chromium.connectOverCDP('http://127.0.0.1:'+(19221+n));const page=browser.contexts()[0].pages().find(p=>p.url().startsWith('vscode-file:'));if(!page)throw Error('QA workbench missing '+n);page.setDefaultTimeout(5000);sessions.push({browser,page});}
 const server=http.createServer(async(req,res)=>{
  try {let raw='';for await(const chunk of req)raw+=chunk;const v=raw?JSON.parse(raw):{};
   if(req.url==='/state'){const result=await Promise.all(sessions.map(async({page},i)=>({node:i+1,url:page.url(),text:(await page.locator('body').innerText()).slice(-4500),frames:page.frames().map(f=>f.url())})));res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));return;}
   const n=Number(v.node||1)-1;if(!sessions[n])throw Error('Invalid node');const started=Date.now();const task=locks[n].then(()=>operate(sessions[n].page,v));locks[n]=task.catch(()=>{});const result=await task;record('action',{request:v,started_ms:started,finished_ms:Date.now(),result});res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));
  }catch(e){record('error',{error:e.message});res.writeHead(500,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}
 });server.listen(18772,'127.0.0.1',()=>console.log('UI ready18772'));
 process.on('SIGTERM',()=>{server.close();log.end();Promise.all(sessions.map(s=>s.browser.close())).finally(()=>process.exit(0));});
})().catch(e=>{console.error(e);process.exit(1)});
