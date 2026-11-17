const {chromium}=require('/home/quangnhathung/.npm/_npx/31e32ef8478fbf80/node_modules/playwright');
const fs=require('fs'),http=require('http');
const state=JSON.parse(fs.readFileSync('/tmp/task011-active.json','utf8')),qa=state.qa,out=state.evidence;
fs.mkdirSync(qa+'/output/playwright',{recursive:true});
const sessions=[];
(async()=>{
for(let n=1;n<=3;n++){
 const browser=await chromium.connectOverCDP('http://127.0.0.1:'+(19221+n));
 const page=browser.contexts()[0].pages().find(p=>p.url().startsWith('vscode-file:'));
 if(!page)throw Error('Workbench missing '+n);sessions.push({browser,page});
}
http.createServer(async(req,res)=>{
try{
 let raw='';for await(const x of req)raw+=x;const v=raw?JSON.parse(raw):{},n=(v.node??1)-1;let result;
 const page=sessions[n]?.page;
 if(req.url==='/state')result=await Promise.all(sessions.map(async({page},i)=>({node:i+1,url:page.url(),text:(await page.locator('body').innerText()).slice(-6500),frames:page.frames().map(f=>f.url())})));
 else if(req.url==='/palette'){await page.keyboard.press('Escape');await page.locator('body').evaluate(b=>{b.tabIndex=-1;b.focus();});await page.keyboard.press('F1');await page.waitForFunction(()=>document.activeElement?.tagName==='INPUT',{},{timeout:7000});result={text:(await page.locator('body').innerText()).slice(-2500)};}
 else if(req.url==='/type'){await page.keyboard.type(v.text);await page.getByText(v.text,{exact:true}).first().waitFor({state:'visible',timeout:7000});result={text:(await page.locator('body').innerText()).slice(-2500)};}
 else if(req.url==='/enter'){await page.keyboard.press('Enter');result={ok:true};}
 else if(req.url==='/frames')result=await Promise.all(page.frames().map(async f=>({url:f.url(),text:await f.locator('body').innerText().catch(()=>''),sliders:await f.getByRole('slider').count()})));
 else if(req.url==='/inspect'){
 const f=page.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode'));if(!f)throw Error('Simulator missing');
 result=await f.locator('body').evaluate(body=>({parts:Array.from(body.querySelectorAll('*')).filter(e=>e.tagName.toLowerCase().startsWith('wokwi-')).map(e=>({tag:e.tagName,id:e.id})),sliders:Array.from(body.querySelectorAll('[role=slider],input[type=range]')).map(e=>({tag:e.tagName,outer:e.outerHTML.slice(0,400)})),text:body.innerText}));
 }
 else if(req.url==='/part'){
 const f=page.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode'));await f.locator(v.part).click();result={text:await f.locator('body').innerText(),sliders:await f.getByRole('slider').evaluateAll(es=>es.map(e=>({outer:e.outerHTML.slice(0,400)})))};
 }
 else if(req.url==='/key'){
 const f=page.frames().find(f=>f.url().startsWith('https://wokwi.com/vscode/wcode'));await f.getByRole('slider').nth(v.index??0).press(v.key);result={text:await f.locator('body').innerText()};
 }
 else if(req.url==='/shot'){await page.screenshot({path:qa+'/output/playwright/'+v.name+'.png'});result={ok:true};}
 else throw Error('Unknown path');
 res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(result));
}catch(e){res.writeHead(500,{'Content-Type':'application/json'});res.end(JSON.stringify({error:e.message}));}
}).listen(18772,'127.0.0.1',()=>console.log('UI controller ready18772'));
})().catch(e=>{console.error(e);process.exit(1)});
