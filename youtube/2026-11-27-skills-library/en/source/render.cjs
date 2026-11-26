const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{
 const T=JSON.parse(fs.readFileSync('timing.json','utf8'));const FPS=25;
 const only=process.argv[2]?process.argv[2].split(',').map(Number):null;
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
 await p.goto('file://'+path.resolve('scene.html'),{waitUntil:'networkidle'});
 await p.evaluate(T=>{window.T=T},T);await p.evaluate(()=>document.fonts.ready);
 if(only){for(const t of only){await p.evaluate(t=>window.render(t),t);await p.screenshot({path:`check_${String(t).replace('.','_')}.jpg`,type:'jpeg',quality:80});}await b.close();return;}
 fs.mkdirSync('frames',{recursive:true});const N=Math.ceil(T.total*FPS);
 for(let i=0;i<N;i++){await p.evaluate(t=>window.render(t),i/FPS);await p.screenshot({path:`frames/f${String(i).padStart(5,'0')}.jpg`,type:'jpeg',quality:92});if(i%250==0)console.log(i,'/',N);}
 await b.close();console.log('done',N);
})();
