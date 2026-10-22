// Run only within the supported cua_repl. No browser network or hidden state.
// `liveDrive`, `liveCal`, `fsPub`, and `fiveRoot` are previously grounded handles.
var liveBase = fiveRoot + '/work/2026-10-22-five-live';
var liveManifest = JSON.parse(await fsPub.readFile(liveBase+'/private/manifest.json','utf8'));
async function saveUI(label,tab,role='audit') {
 const state=await tab.getAXState({emit:false,disableDiffing:true});
 const record={time:new Date().toISOString(),role,url:await tab.url(),state};
 await fsPub.writeFile(liveBase+'/private/ui-'+label+'.json',JSON.stringify(record,null,2));
 return state;
}
async function renameLive(alias,from,to,label) {
 const oldName='FIVE-LIVE-20261022-Q7K '+alias+' '+from;
 const newName='FIVE-LIVE-20261022-Q7K '+alias+' '+to;
 const before=await saveUI(label+'-before',liveDrive);
 if(!before.includes(oldName)) throw Error('Expected old name absent: '+label);
 await fsPub.writeFile(liveBase+'/private/dispatch-'+label+'.json',JSON.stringify({time:new Date().toISOString(),alias,action:'rename',oldName,newName}));
 await liveDrive.playwright.getByRole('row',{name:new RegExp('^'+oldName+' Folder')}).click({button:'right'});
 const menu=await saveUI(label+'-menu',liveDrive);
 if(!menu.includes('Rename'))throw Error('No Rename menu');
 await liveDrive.playwright.getByRole('menuitem',{name:/^Rename/}).click();
 const edit=await saveUI(label+'-edit',liveDrive);
 if(!edit.includes(oldName))throw Error('Rename field mismatch');
 await liveDrive.playwright.getByRole('textbox',{name:'Rename',exact:true}).fill(newName);
 await liveDrive.playwright.getByRole('button',{name:'OK',exact:true}).click();
 await saveUI(label+'-sent',liveDrive);
 await liveDrive.reload();
 const after=await saveUI(label+'-reload',liveDrive);
 if(!after.includes(newName))throw Error('Reload did not show new name');
 return {label,alias,newName,uiReloadMatch:true};
}
async function openLiveCal(alias,label) {
 const m=liveManifest['calendar:'+alias];
 if(!m)throw Error('Unlisted fixture');
 await liveCal.goto(m.url);
 let state=await saveUI(label+'-open',liveCal);
 if(!state.includes('Edit event')) {
  // A new navigation can first expose loading placeholders. This is one bounded read-only check.
  state=await saveUI(label+'-ready',liveCal);
 }
 if(!state.includes('FIVE-LIVE-20261022-Q7K '+alias))throw Error('Event identity title absent');
 await liveCal.playwright.getByRole('button',{name:'Edit event',exact:true}).click();
 state=await saveUI(label+'-editor',liveCal);
 if(!state.includes('Description: Title'))state=await saveUI(label+'-editor-ready',liveCal);
 return state;
}
async function changeLiveCal(alias,field,value,label) {
 const state=await openLiveCal(alias,label);
 if(!state.includes('Description: All day, Value: 1'))throw Error('All-day contract not visible');
 if(!state.includes('Value: Free') || !state.includes('Value: Private'))throw Error('Privacy/free contract not visible');
 const fields={title:['textbox','Title'],location:['combobox','Add location'],description:['textbox','Description']};
 if(!fields[field])throw Error('Unlisted field');
 const [role,name]=fields[field];
 await fsPub.writeFile(liveBase+'/private/dispatch-'+label+'.json',JSON.stringify({time:new Date().toISOString(),alias,field,value,url:await liveCal.url()}));
 await liveCal.playwright.getByRole(role,{name,exact:true}).fill(value);
 await liveCal.playwright.getByRole('button',{name:'Save',exact:true}).click();
 await saveUI(label+'-sent',liveCal);
 return {label,alias,field,value,saveDispatched:true};
}
