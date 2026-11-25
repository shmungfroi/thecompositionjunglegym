const {load}=require('./harness.js');const f=process.argv[2]||'index.html';
const cases=[[{}, 'fresh'],[{cjg_stage:'4'},'stage4'],[{cjg_stage:'5'},'stage5'],[{cjg_stage:'6'},'stage6'],[{cjg_stage:'7'},'stage7 (invalid)'],[{cjg_stage:'3'},'stage3 (invalid)'],
 [{cjg_stage:'6',cjg_level:'2'},'level2 + stage6'],[{cjg_stage:'4',cjg_level:'0'},'level0 invalid + stage4'],[{cjg_stage:'5',cjg_level:'abc'},'level abc + stage5'],[{cjg_stage:'5',cjg_level:'9'},'level 9 + stage5'],[{cjg_level:'7'},'level7'],[{cjg_level:'1'},'level1'],
 [{cjg_level:'3.5'},'level 3.5'],[{cjg_stage:'4',cjg_level:''},'level empty + stage4'],[{cjg_level:'4'},'level4 no stage (a NEW level 4, must not be migrated)']];
for(const [ls,name] of cases){const r=load(f,ls);const S=r.get('S');console.log(name.padEnd(52),'-> S.level',S.level,'| stored cjg_level',r.store.cjg_level,'| cjg_stage',r.store.cjg_stage,'| err',r.err&&r.err.message)}
// second load after migration: stays put (one-time)
const r1=load(f,{cjg_stage:'6'});const r2=load(f,{...r1.store});console.log('reload after migration: level',r2.get('S').level,'(expect 5, not re-migrated to LVMIG[5]=4)');
// user then picks level 6 after migration, reload
r1.run("lvlSet(6)");const r3=load(f,{...r1.store});console.log('after migration, choose 6, reload: level',r3.get('S').level,'(expect 6; must NOT become 5)');
console.log('LVN',JSON.stringify(r1.get('LVN')),'LVMIG',JSON.stringify(r1.get('LVMIG')));
