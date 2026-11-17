async (page) => {
 await page.getByRole('link',{name:'Phiên thực nghiệm',exact:true}).click();
 await page.waitForFunction(()=>!document.getElementById('startExperiment').disabled);
 await page.locator('#experimentName').fill('TASK-010 QA · pending restart');
 await page.locator('#experimentConfig').fill('{"source":"live Wokwi VSCode","scope":"TASK-010 pending restart"}');
 const start=page.waitForResponse(r=>r.url().endsWith('/api/experiments')&&r.request().method()==='POST');
 await page.locator('#startExperiment').click();const started=await start;const experiment=await started.json();if(started.status()!==201)throw Error(JSON.stringify(experiment));
 await page.getByRole('link',{name:'Điều khiển node',exact:true}).click();
 await page.request.post('http://127.0.0.1:18765/proxy',{data:{mode:'drop_ack'}});
 await page.locator('#controlMode').selectOption('AUTO');await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
 const sending=page.waitForResponse(r=>r.url().endsWith('/api/nodes/node_01/commands')&&r.request().method()==='POST');
 await page.locator('#applyCommand').click();const command=await (await sending).json();
 const before=await (await page.request.get('http://127.0.0.1:8001/api/commands/'+command.command_id)).json();if(before.result!=='PENDING')throw Error('Command not pending before restart');
 const restart=await page.request.post('http://127.0.0.1:18766/backend/restart');if(!restart.ok())throw Error('QA backend restart failed');const processes=await restart.json();
 await page.waitForFunction(()=>document.getElementById('commandFeedback').textContent.includes('BACKEND_RESTART'),{},{timeout:20000});
 const after=await (await page.request.get('http://127.0.0.1:8001/api/commands/'+command.command_id)).json();if(after.result!=='TIMEOUT'||after.reason!=='BACKEND_RESTART')throw Error(JSON.stringify(after));
 await page.waitForFunction(()=>!document.getElementById('applyCommand').disabled);
 await page.screenshot({path:'output/playwright/ui-backend-restart-live.png',fullPage:true});
 await page.request.post('http://127.0.0.1:18765/proxy',{data:{mode:'passthrough'}});
 await page.getByRole('link',{name:'Phiên thực nghiệm',exact:true}).click();await page.reload();
 await page.waitForFunction(()=>document.getElementById('experimentList').textContent.includes('TASK-010 QA'));
 await page.locator('[data-experiment="'+experiment.id+'"]').click();
 await page.waitForFunction(()=>!document.getElementById('stopExperiment').disabled);
 const restored=await (await page.request.get('http://127.0.0.1:8001/api/experiments/'+experiment.id)).json();if(restored.ended_at)throw Error('Open experiment not restored');
 await page.screenshot({path:'output/playwright/ui-open-experiment-restored-live.png',fullPage:true});
 await page.locator('#stopExperiment').click();await page.waitForFunction(()=>document.getElementById('experimentActionMessage').textContent.includes('Phiên đã dừng'));
 const result={experiment_id:experiment.id,command_id:command.command_id,before:before.result,after:after.result,reason:after.reason,processes,open_experiment_restored_after_reload:true,experiment_stopped:true};
 await page.request.post('http://127.0.0.1:18765/events',{data:{event:'pending_restart_result',...result}});return result;
}
