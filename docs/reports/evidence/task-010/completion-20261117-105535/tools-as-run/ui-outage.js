async (page) => {
 await page.getByRole('link',{name:'Điều khiển node',exact:true}).click();
 await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
 const node=await(await page.request.get('http://127.0.0.1:8001/api/nodes')).json();const initial=node.find(x=>x.node_id==='node_01');
 if(initial.telemetry.environment!=='NIGHT'||initial.telemetry.mode!=='AUTO')throw Error('Need AUTO NIGHT baseline');
 await page.request.post('http://127.0.0.1:18765/proxy',{data:{mode:'drop_ack'}});
 await page.locator('#controlMode').selectOption('AUTO');
 const sent=page.waitForResponse(r=>r.url().endsWith('/api/nodes/node_01/commands')&&r.request().method()==='POST');await page.locator('#applyCommand').click();const response=await sent;const command=await response.json();if(response.status()!==202)throw Error(JSON.stringify(command));
 const stopped=await page.request.post('http://127.0.0.1:18766/broker/stop');if(!stopped.ok())throw Error('Broker QA stop failed');const action=await stopped.json();
 await page.waitForFunction(()=>document.getElementById('applyCommand').disabled&&document.getElementById('apiBadge').textContent!=='Máy chủ sẵn sàng');
 await page.screenshot({path:'output/playwright/ui-broker-offline-live.png',fullPage:true});
 const result={event:'broker_outage_started',command_id:command.command_id,boot_id:initial.telemetry.boot_id,initial:initial.telemetry,action,feedback:await page.locator('#commandFeedback').innerText(),locked:await page.locator('#applyCommand').isDisabled()};
 await page.request.post('http://127.0.0.1:18765/events',{data:result});return result;
}
