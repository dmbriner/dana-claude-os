const fs=require('fs');const html=fs.readFileSync(process.argv[2],'utf8');
const data=html.match(/<script type="application\/json" id="dossier-data">([\s\S]*?)<\/script>/)[1];
const js=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
const el=()=>({innerHTML:'',textContent:'',style:{},classList:{add(){},remove(){},toggle(){},contains(){return false}},addEventListener(){},setAttribute(){},appendChild(){},querySelector:()=>el(),querySelectorAll:()=>[],closest:()=>null,dataset:{}});
const store={};const main=el();
global.document={getElementById:id=>id==='dossier-data'?{textContent:data}:(store[id]=store[id]||el()),querySelector:()=>main,querySelectorAll:()=>[],createElement:el,addEventListener(){},documentElement:el(),body:el(),title:''};
global.window={addEventListener(){},matchMedia:()=>({matches:false,addEventListener(){}}),localStorage:{getItem:()=>null,setItem(){}}};global.localStorage=window.localStorage;global.location={hash:''};global.IntersectionObserver=function(){return{observe(){}}};
try{eval(js);const big=Object.values(store).map(e=>e.innerHTML.length).reduce((a,b)=>a+b,0)+main.innerHTML.length;console.log('OK rendered chars:',big, 'sections:', (Object.values(store).map(e=>e.innerHTML).join('')+main.innerHTML).match(/<section id="[a-z-]+"/g)?.join(' '));}catch(e){console.log('ERR',e.stack.split('\n').slice(0,3).join(' | '))}
