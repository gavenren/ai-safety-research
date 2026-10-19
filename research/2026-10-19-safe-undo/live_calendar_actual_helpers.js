async(type,data)=>{let r={id:'UC-'+String(++ucSeq).padStart(5,'0'),phase:ucPhase,token:ucToken,utc:new Date().toISOString(),type,...data};await undoFs.appendFile(undoCalDir+'/actions.jsonl',JSON.stringify(r)+'\n');return r;}

async(label,emit=true)=>{let state=await undoCalTab.playwright.domSnapshot();let r=await ucRecord('observation',{label,url:await undoCalTab.url(),tab_id:undoCalTab.id,state});ucLast=r.id;if(emit)console.log({id:r.id,state:state.includes('- main:')?state.slice(state.indexOf('- main:')):state});return r;}

async(label,args,fn)=>{let start=new Date().toISOString(),before=ucLast,error=null;try{await fn()}catch(e){error=String(e)}let after=await ucObs(label+'_after',false);let r=await ucRecord('action',{label,args,start,end:new Date().toISOString(),before,after:after.id,error});console.log({id:r.id,label,error});if(error)throw Error(error);return r;}

async(name)=>{await undoFs.writeFile(undoCalDir+'/'+name+'.png',await undoCalTab.screenshot({fullPage:false}));await ucRecord('screenshot',{file:name+'.png',source:ucLast});}

async(label)=>{let r={url:await undoCalTab.url(),title:await undoCalTab.playwright.getByRole('textbox',{name:'Title',exact:true}).getAttribute('value'),x:await undoCalTab.playwright.getByRole('textbox',{name:'Description',exact:true}).innerText(),show_as:await undoCalTab.playwright.getByRole('combobox',{name:'Show as',exact:true}).innerText(),visibility:await undoCalTab.playwright.getByRole('combobox',{name:'Visibility',exact:true}).innerText()};await ucRecord('saved_fields',{label,...r});console.log(r);return r;}