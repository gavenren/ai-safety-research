async(kind,label,extra={})=>{var row={id:'NU-'+String(++S.seq).padStart(5,'0'),phase:S.phase,trial:S.current||null,kind,label,utc:new Date().toISOString(),...extra};await fs.appendFile(S.dir+'/actions.jsonl',JSON.stringify(row)+'\n');return row;}

async(label,emit=true)=>{var state=await nt.playwright.domSnapshot();var row=await nr('observation',label,{url:await nt.url(),state});if(emit)nodeRepl.write({id:row.id,label,state:state.slice(state.indexOf('- main:'))});return row;}

async(label,fn,args={})=>{var before=await ns(label+' before',false),start=new Date().toISOString(),error=null;try{await fn();}catch(e){error=String(e);}var a=await nr('action',label,{started:start,ended:new Date().toISOString(),args,before:before.id,error});var after=await ns(label+' after',false);nodeRepl.write({action_id:a.id,state_id:after.id,label,error,state:after.state.slice(after.state.indexOf('- main:'))});if(error)throw Error(error);return after;}

async(label)=>{var b=await nt.screenshot({fullPage:false});await fs.writeFile(S.dir+'/images/'+label+'.png',b);return nr('image',label,{file:'images/'+label+'.png',sha256:crypto.createHash('sha256').update(b).digest('hex')});}

async(label)=>{var raw=await ns(label+' DOM',false),title=await nt.playwright.getByRole('main').getByRole('textbox',{name:'',exact:true}).textContent(),x=await nt.playwright.getByRole('row',{name:'X',exact:true}).getByRole('button').innerText(),y=await nt.playwright.getByRole('row',{name:'Y',exact:true}).getByRole('checkbox').evaluate(el=>el.checked); var r=await nr('saved_fields',label,{source:raw.id,url:raw.url,values:{title,x,y,body_empty:raw.state.includes('Press ‘enter’ to continue with an empty page, or')}}); nodeRepl.write(r);return r;}

async(value,label)=>{await na(label+' open X',()=>nt.playwright.getByRole('row',{name:'X',exact:true}).getByRole('button').click(),{});await na(label+' fill X',()=>nt.playwright.getByRole('dialog',{name:'',exact:true}).getByRole('textbox').fill(String(value)),{value});await na(label+' blur X',()=>nt.playwright.getByRole('main').getByRole('textbox',{name:'',exact:true}).click());await ni(label+'-before-reload');}

async(label)=>{await na(label+' reload',()=>nt.reload());await na(label+' ready',()=>nt.playwright.getByRole('banner').getByRole('button',{name:'Actions',exact:true}).waitFor({state:'visible',timeoutMs:10000}));return nread(label+' saved');}