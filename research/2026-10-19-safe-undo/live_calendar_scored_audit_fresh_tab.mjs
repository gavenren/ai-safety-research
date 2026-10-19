export function createAudit({tab,fs,dir}) {
  let seq=0,last=null,ctx={trial_id:null,token:null,phase:'scored'};
  const now=()=>new Date().toISOString();
  async function record(type,data){const r={id:'UCN-'+String(++seq).padStart(5,'0'),...ctx,utc:now(),type,...data};await fs.appendFile(dir+'/actions.jsonl',JSON.stringify(r)+'\n');return r;}
  async function obs(label,emit=false){const state=await tab.playwright.domSnapshot();const r=await record('observation',{label,url:await tab.url(),tab_id:tab.id,state});last=r.id;if(emit)console.log({id:r.id,state});return r;}
  async function act(label,args,fn){const start=now(),before=last;let error=null;try{await fn()}catch(e){error=String(e)}const after=await obs(label+'_after');const r=await record('action',{label,args,start,end:now(),before,after:after.id,error});if(error){console.log({id:r.id,label,error});throw Error(error)}return r;}
  async function shot(name){await fs.writeFile(dir+'/'+name+'.png',await tab.screenshot({fullPage:false}));return record('screenshot',{file:name+'.png',source:last});}
  function setContext(a){ctx={trial_id:a.trial_id,token:a.token,phase:'scored'};}
  return {record,obs,act,shot,setContext};
}
