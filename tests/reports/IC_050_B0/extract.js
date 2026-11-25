// Extracts the main <script> of a given html and evaluates named consts with a stubbed DOM-less approach:
// we slice specific const literals by bracket matching, then eval them standalone.
const fs=require('fs');
function sliceConst(src,name){
  const re=new RegExp('(?:const|let|var)\\s+'+name+'\\s*=\\s*');const m=re.exec(src);if(!m)return null;
  let i=m.index+m[0].length;const open=src[i];const close={'[':']','{':'}'}[open];if(!close)return null;
  let depth=0,inS=null,j=i;
  for(;j<src.length;j++){const c=src[j];
    if(inS){if(c==='\\'){j++;continue}if(c===inS)inS=null;continue}
    if(c==="'"||c==='"'||c==='`'){inS=c;continue}
    if(c==='['||c==='{'||c==='(')depth++;
    if(c===']'||c==='}'||c===')'){depth--;if(depth===0){j++;break}}
  }
  return {text:src.slice(i,j),line:src.slice(0,m.index).split('\n').length};
}
module.exports={sliceConst,read:f=>fs.readFileSync(f,'utf8')};
