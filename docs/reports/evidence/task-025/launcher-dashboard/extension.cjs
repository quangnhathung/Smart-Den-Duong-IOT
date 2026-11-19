const vscode=require('vscode'),fs=require('node:fs'),path=require('node:path');
exports.activate=async()=>{
const folder=vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
const root='/home/quangnhathung/HungQuang_WorkSpace/Learing/Iot/DoAn';
const role=path.basename(folder||'');
if(![root+'/firmware/simulations/node_01',root+'/firmware/simulations/node_02',root+'/firmware/simulations/node_03',root+'/dashboard'].includes(folder))return;
const report={folder,at:new Date().toISOString(),status:'STARTING'};
const save=()=>fs.writeFileSync(root+'/firmware/output/task-025/'+role+'-launcher.json',JSON.stringify(report,null,2));save();
try{
const id=role==='dashboard'?'ritwickdey.liveserver':'wokwi.wokwi-vscode';
const ext=vscode.extensions.all.find(e=>e.id.toLowerCase()===id);if(!ext)throw Error('Missing extension '+id);
await ext.activate();report.extension=ext.id;report.status='EXTENSION_ACTIVE';save();
if(role==='dashboard'){
await vscode.window.showTextDocument(vscode.Uri.file(path.join(folder,'index.html')));
await vscode.commands.executeCommand('extension.liveServer.goOnline',vscode.Uri.file(path.join(folder,'index.html')));
}else{await vscode.commands.executeCommand('wokwi-vscode.start');}
report.status='START_COMMAND_COMPLETED';save();
}catch(e){report.status='ERROR';report.error=String(e);save();}
};exports.deactivate=()=>{};
