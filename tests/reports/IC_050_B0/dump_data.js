// Evaluates every top-level data literal (const X=[...]/{...}, and X.y={...}) in old and new index.html,
// finds every object that carries a level `l`, and writes: (a) all tagged items new, (b) property-by-property old/new comparison.
const fs=require('fs');
function literals(src){
  const out={};const re=/(?:^|[\n;])\s*(?:(?:const|let|var)\s+([A-Za-z_$][\w$]*)|([A-Z][\w$]*\.[\w$]+))\s*=\s*(?=[\[{])/g;let m;
  while((m=re.exec(src))){const name=m[1]||m[2];let i=m.index+m[0].length;let depth=0,inS=null,j=i,tpl=0;
    for(;j<src.length;j++){const c=src[j];
      if(inS){if(c==='\\'){j++;continue}if(c===inS)inS=null;continue}
      if(c==='/'&&src[j+1]==='/'){while(j<src.length&&src[j]!=='\n')j++;continue}
      if(c==='/'&&src[j+1]==='*'){j=src.indexOf('*/',j)+1;continue}
      if(c==="'"||c==='"'||c==='`'){inS=c;continue}
      if(c==='['||c==='{'||c==='(')depth++;
      if(c===']'||c==='}'||c===')'){depth--;if(depth===0){j++;break}}
    }
    const text=src.slice(i,j);if(!/\bl:\s*\d/.test(text))continue;
    out[name]={text,line:src.slice(0,m.index+1).split('\n').length+ (src[m.index]==='\n'?0:0)};
  }
  return out;
}
function tryEval(text){try{return (0,eval)('('+text+')')}catch(e){return {__err:String(e).slice(0,80)}}}
function walk(v,path,acc){if(!v||typeof v!=='object')return;
  if(!Array.isArray(v)&&Object.prototype.hasOwnProperty.call(v,'l')&&typeof v.l==='number')acc.push({path,o:v});
  for(const k of Object.keys(v)){walk(v[k],path+(Array.isArray(v)?`[${v[k]&&v[k].k!==undefined?v[k].k:(v[k]&&v[k].n)||k}]`:'.'+k),acc)}}
const ser=x=>JSON.stringify(x,(k,v)=>typeof v==='function'?'fn:'+v.toString():v);
const res={};
for(const [tag,f] of [['old',process.argv[2]],['new',process.argv[3]]]){
  const src=fs.readFileSync(f,'utf8');const L=literals(src);res[tag]={};
  for(const n of Object.keys(L)){const v=tryEval(L[n].text);const acc=[];if(v&&v.__err){res[tag][n]={err:v.__err,line:L[n].line,raw:L[n].text};continue}walk(v,n,acc);
    res[tag][n]={line:L[n].line,items:acc.map(a=>({path:a.path,l:a.o.l,stp:a.o.stp,s:a.o.s,n:a.o.n,k:a.o.k,props:Object.fromEntries(Object.keys(a.o).map(k=>[k,ser(a.o[k])]))}))}}
}
fs.writeFileSync(process.argv[4],JSON.stringify(res,null,1));
for(const n of new Set([...Object.keys(res.old),...Object.keys(res.new)])){const a=res.old[n],b=res.new[n];
  console.log(n,'old:',a?(a.err?'ERR '+a.err:a.items.length+' @'+a.line):'-','new:',b?(b.err?'ERR '+b.err:b.items.length+' @'+b.line):'-')}
