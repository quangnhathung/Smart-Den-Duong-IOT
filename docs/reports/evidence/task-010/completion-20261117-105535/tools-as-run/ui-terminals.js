async (page) => {
 const result=[];
 await page.setViewportSize({width:1440,height:950});
 await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
 await page.evaluate(()=>{const p=document.createElement('div');p.textContent='KIỂM TRA TÍCH HỢP LIVE · NODE_01 · MQTT/ACK THẬT';p.style.cssText='background:#fef3c7;padding:8px;text-align:center';document.getElementById('main').prepend(p);});
 for(const mode of ['expired','hold_ack']) {
  const arm=await page.request.post('http://127.0.0.1:18765/proxy',{data:{mode}});if(!arm.ok())throw Error('Proxy arm failed');
  await page.locator('#controlMode').selectOption('AUTO');
  await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
  const responsePromise=page.waitForResponse(r=>r.url().endsWith('/api/nodes/node_01/commands')&&r.request().method()==='POST');
  await page.locator('#applyCommand').click();
  const response=await responsePromise;const command=await response.json();if(response.status()!==202)throw Error(JSON.stringify(command));
  const expected=mode==='expired'?'Node từ chối':'Máy chủ hết thời gian';
  await page.waitForFunction(value=>document.getElementById('commandFeedback').textContent.includes(value),expected,{timeout:25000});
  const outcome=await page.request.get('http://127.0.0.1:8001/api/commands/'+command.command_id);const final=await outcome.json();
  const feedback=await page.locator('#commandFeedback').innerText();
  await page.screenshot({path:'output/playwright/ui-'+mode+'-live.png',fullPage:true});
  await page.request.post('http://127.0.0.1:18765/events',{data:{event:'ui_terminal',command_id:command.command_id,feedback,api:final,visibility:await page.evaluate(()=>document.visibilityState)}});
  result.push({mode,command_id:command.command_id,result:final.result,reason:final.reason,attempts:final.attempts,feedback});
  if(mode==='hold_ack') {
   await page.waitForTimeout(2800);
   const late=await (await page.request.get('http://127.0.0.1:8001/api/commands/'+command.command_id)).json();if(late.result!=='TIMEOUT')throw Error('Late ACK changed final result');
  }
  await page.request.post('http://127.0.0.1:18765/proxy',{data:{mode:'passthrough'}});
 }
 return result;
}
