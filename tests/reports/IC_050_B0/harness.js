// Loads the app's single inline <script> in node with a permissive DOM stub (no browser). Returns a vm context.
// Top-level const/let are exposed by appending an export line that evals names on demand: ctx.__get('NAME').
const fs=require('fs'),vm=require('vm');
function load(file,ls={}){
  const html=fs.readFileSync(file,'utf8');const a=html.indexOf('<script>',html.indexOf('</script>'))+8,b=html.lastIndexOf('</script>');
  const src=html.slice(a,b)+'\n;globalThis.__get=function(n){return eval(n)};globalThis.__run=function(code){return eval(code)};';
  const store={...ls};
  const mk=()=>{const f=function(){};return new Proxy(f,{get(t,p){if(p===Symbol.toPrimitive)return()=>'';if(p==='then')return undefined;if(p==='length')return 0;if(p==='nextNode')return()=>null;if(p===Symbol.iterator)return function*(){};
      if(p==='dataset'||p==='style'||p==='classList')return t[p]||(t[p]=mk());if(p in t)return t[p];
      if(p==='forEach'||p==='map'||p==='filter')return()=>[];if(p==='value'||p==='textContent'||p==='innerHTML')return'';
      if(p==='querySelectorAll'||p==='getElementsByTagName'||p==='children')return()=>[];if(p==='closest')return()=>null;if(p==='querySelector'||p==='getElementById')return()=>mk();
      return mk()},set(t,p,v){t[p]=v;return true},apply(){return mk()},construct(){return mk()}})};
  const localStorage={getItem:k=>k in store?String(store[k]):null,setItem:(k,v)=>{store[k]=String(v)},removeItem:k=>{delete store[k]},_store:store};
  const document=mk();document.querySelectorAll=()=>[];document.querySelector=()=>mk();document.getElementById=()=>mk();document.addEventListener=()=>{};document.createElement=()=>mk();
  const ctx={console,localStorage,document,navigator:{userAgent:'node'},location:{hash:'',search:'',href:''},performance:{now:()=>0},setTimeout:()=>0,setInterval:()=>0,clearTimeout(){},clearInterval(){},requestAnimationFrame:()=>0,
    addEventListener(){},removeEventListener(){},matchMedia:()=>({matches:false,addEventListener(){},addListener(){}}),fetch:()=>new Promise(()=>{}),AudioContext:function(){return mk()},Audio:function(){return mk()},Image:function(){return mk()},history:{replaceState(){},pushState(){}},
    innerWidth:1366,innerHeight:768,scrollTo(){},getComputedStyle:()=>mk(),URL,URLSearchParams,TextEncoder,TextDecoder,Blob:function(){},FileReader:function(){return mk()},ResizeObserver:function(){return mk()},MutationObserver:function(){return mk()},IntersectionObserver:function(){return mk()},speechSynthesis:mk(),screen:{width:1366,height:768},devicePixelRatio:1,NodeFilter:{SHOW_ELEMENT:1,SHOW_TEXT:4,FILTER_REJECT:2,FILTER_SKIP:3,FILTER_ACCEPT:1},alert(){},confirm:()=>true,prompt:()=>null,Math,JSON,Date};
  ctx.window=ctx;ctx.self=ctx;ctx.globalThis=ctx;vm.createContext(ctx);
  let err=null;try{vm.runInContext(src,ctx,{filename:file})}catch(e){err=e}
  return{ctx,err,store,get:n=>ctx.__get?ctx.__get(n):undefined,run:c=>ctx.__run(c)};
}
module.exports={load};
if(require.main===module){const r=load(process.argv[2]);console.log('load error:',r.err&&(r.err.stack||'').split('\n').slice(0,4).join(' | '));try{console.log('S.level',r.get('S').level,'LVN',r.get('LVN'))}catch(e){console.log('get failed',String(e))}}
