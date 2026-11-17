const liveServer=require('/home/quangnhathung/.vscode/extensions/ritwickdey.liveserver-5.7.10/node_modules/live-server');
liveServer.start({root:'/tmp/task010-completion/dashboard',host:'127.0.0.1',port:5500,open:false,logLevel:1,ignore:['**/output/**','**/.playwright-cli/**','**/tests/**','**/*.md']});
process.on('SIGTERM',()=>{liveServer.shutdown();process.exit(0);});
