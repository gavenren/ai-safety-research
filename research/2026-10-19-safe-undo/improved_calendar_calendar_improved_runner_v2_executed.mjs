// Browser runner for the frozen prospective study. Mutations use visible UI only.
// Each public method is one bounded phase. Call methods separately.
export async function createCalendarRunner({tab,fs,dir,prepare,finish,prefix='CUI'}) {
  let seq=0,last=null,row=null;
  try{const old=(await fs.readFile(dir+'/actions.jsonl','utf8')).trim().split('\n');seq=old.filter(Boolean).length;}catch{}
  const now=()=>new Date().toISOString();
  const role=(r,n)=>tab.playwright.getByRole(r,{name:n,exact:true});
  const context=()=>({trial_id:row?.trial_id??null,marker:row?.assignment?.marker??null});
  async function record(type,data){const r={id:prefix+'-'+String(++seq).padStart(6,'0'),...context(),utc:now(),type,...data};await fs.appendFile(dir+'/actions.jsonl',JSON.stringify(r)+'\n');return r;}
  async function obs(label){const state=await tab.playwright.domSnapshot();const r=await record('observation',{label,url:await tab.url(),tab_id:tab.id,state});last=r.id;return r;}
  async function action(label,args,fn){
    const start=now(),before=last,attempt=await record('action_attempt',{label,args,start,before});let error=null,result=null,observation_error=null,after=null;
    try{result=await fn()}catch(e){error=String(e)}
    try{after=(await obs(label+'_after')).id}catch(e){observation_error=String(e)}
    const out=await record('action_result',{label,args,attempt_id:attempt.id,start,end:now(),before,after,error,observation_error,result:result??null});
    if(error||observation_error)throw Error('Action '+label+': '+(error||observation_error));return out;
  }
  async function checkpoint(label){if(!row)return;row.last_checkpoint=label;row.checkpoint_utc=now();await fs.writeFile(dir+'/'+row.trial_id+'.checkpoint.json',JSON.stringify(row,null,2));}
  async function shot(name){await fs.writeFile(dir+'/'+name+'.png',await tab.screenshot({fullPage:false}));return record('screenshot',{file:name+'.png',source:last});}
  async function readyEditor(){await role('textbox','Description').waitFor({state:'visible',timeoutMs:15000});await tab.playwright.getByRole('progressbar').waitFor({state:'hidden',timeoutMs:15000});}
  async function fields(label,reloaded=true){
    await readyEditor();const dom=await obs(label+'_dom');
    const raw={url:await tab.url(),title:await role('textbox','Title').evaluate(el=>el.value),
      x_raw:await role('textbox','Description').innerText(),y_raw:await role('combobox','Show as').innerText(),
      start:await role('textbox','Start date').evaluate(el=>el.value),end:await role('textbox','End date').evaluate(el=>el.value),
      all_day:await role('checkbox','All day').evaluate(el=>el.checked),visibility:await role('combobox','Visibility').innerText(),
      recurrence:await role('combobox','Recurrence').innerText(),guests:await role('combobox','Guests').evaluate(el=>el.value),
      guest_panel:await role('tabpanel','Guests').innerText(),notifications:await role('list','Notifications').innerText(),
      location:await role('combobox','Add location').evaluate(el=>el.value),conference_absent:await role('button','Add Google Meet video conferencing').count()===1};
    const text=raw.x_raw.replace(/^[\r\n]+|[\r\n]+$/g,'');
    const checks={dates:raw.start==='Oct 14, 2026'&&raw.end==='Oct 14, 2026',all_day:raw.all_day===true,private:raw.visibility==='Private',
      no_recurrence:raw.recurrence==='Does not repeat',no_guests:raw.guests===''&&raw.guest_panel.trim()==='Guest permissions\nModify event\nInvite others\nSee guest list',
      no_notifications:raw.notifications==='',no_location:raw.location==='',no_conference:raw.conference_absent};
    const v={x:/^-?\d+$/.test(text)&&Number.isSafeInteger(Number(text))?Number(text):null,y:raw.y_raw==='Free'?0:raw.y_raw==='Busy'?1:null,
      x_raw:raw.x_raw,y_raw:raw.y_raw,identity:raw.url,native_id:raw.url,marker:row.assignment.marker,
      identity_ok:raw.title===row.assignment.marker&&raw.url===row.native_id,contract:Object.values(checks).every(Boolean),
      contract_ok:Object.values(checks).every(Boolean),checks,raw,reloaded,utc:now()};
    const r=await record('saved_fields',{label,...v,source_observation:dom.id});v.evidence_id=r.id;v.readId=r.id;v.readAt=v.utc;
    if(!v.identity_ok||!v.contract||v.x===null||v.y===null)throw Error('Invalid saved identity, fields or contract at '+label);return v;
  }
  async function reopen(label){
    if(await tab.url()===row.native_id)await action(label+'_reload',{},()=>tab.reload());
    else await action(label+'_open',{url:row.native_id},()=>tab.goto(row.native_id));
    return fields(label,true);
  }
  async function save(label){
    await action(label+'_save',{},()=>role('button','Save').click());
    await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});
    await tab.playwright.getByText('Event saved',{exact:true}).first().waitFor({state:'visible',timeoutMs:15000});
    await obs(label+'_notice');return reopen(label+'_saved');
  }
  async function literal(label,x,y,{force=false,expected=null}={}){
    const before=await fields(label+'_before',false);
    if(expected&&(before.x!==expected.x||before.y!==expected.y))throw Error('Unexpected saved change before '+label);
    if(force||before.x!==x)await action(label+'_x',{literal:String(x)},()=>role('textbox','Description').fill(String(x)));
    if(before.y!==y){await action(label+'_availability',{},()=>role('combobox','Show as').click());await action(label+'_y',{literal:y?'Busy':'Free'},()=>role('option',y?'Busy':'Free').click());}
    if(!force&&before.x===x&&before.y===y)return reopen(label+'_no_op');return save(label);
  }
  async function exactSearch(marker,label){
    if(await role('combobox','Search').count()===0)await action(label+'_open_search',{},()=>role('button','Search').click());
    await action(label+'_query',{marker},async()=>{await role('combobox','Search').fill(marker);await role('combobox','Search').press('Enter');});
    await tab.playwright.getByRole('progressbar').waitFor({state:'hidden',timeoutMs:15000});return obs(label+'_ready');
  }
  async function fail(e,label){row.status='unknown';row.reason=String(e);row.failed_phase=label;await record('phase_error',{label,error:String(e)});await checkpoint(label+'_failed');console.log({trial_id:row.trial_id,phase:label,error:row.reason});return {ok:false,trial_id:row.trial_id,phase:label};}
  async function guarded(label,fn){if(!row&&label!=='begin')throw Error('No current trial');if(row?.failed_phase&&label!=='cleanup')throw Error('Trial already stopped');
    if(row&&Date.now()-Date.parse(row.started_at)>720000&&label!=='cleanup')return fail('12-minute trial limit',label);
    try{await fn();await checkpoint(label);console.log({trial_id:row.trial_id,phase:label,ok:true});return {ok:true,trial_id:row.trial_id,phase:label};}catch(e){return fail(e,label);}}
  async function begin(a){
    row={trial_id:a.trial_id,assignment:a,site:'calendar',started_at:now(),status:'unknown',reason:null,native_id:null,later_phases:[],final_reads:[],write_attempts:0,uncertain_saves:0};
    await record('trial_start',{assignment:a});await checkpoint('started');
    return guarded('begin',async()=>{
      const initial=await obs('creation_ready');
      if(initial.state.includes('- heading "Search"'))await action('leave_search',{},()=>role('button','Go back').click());
      await tab.playwright.getByRole('progressbar').waitFor({state:'hidden',timeoutMs:15000});
      if(!await role('button','Create').isEnabled())throw Error('Calendar is not ready for creation');
      await action('create_menu',{},()=>role('button','Create').click());await action('new_event',{},()=>role('menuitem','Event').click());
      await action('full_editor',{},()=>role('button','More options').click());await action('title',{value:a.marker},()=>role('textbox','Title').fill(a.marker));
      await action('all_day',{value:true},()=>role('checkbox','All day').check());
      for(const name of ['Start date','End date'])await action(name,{value:'Oct 14, 2026'},async()=>{await role('textbox',name).fill('Oct 14, 2026');await role('textbox',name).press('Tab');});
      await action('baseline_x',{value:'0'},()=>role('textbox','Description').fill('0'));
      const n=await role('button','Remove notification').count();for(let i=0;i<n;i++)await action('remove_notification',{index:i},()=>role('button','Remove notification').first().click());
      await action('visibility_menu',{},()=>role('combobox','Visibility').click());await action('private',{},()=>role('option','Private').click());
      row.creation_attempted=true;await checkpoint('before_create_save');await action('create_save',{},()=>role('button','Save').click());
      await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});await tab.playwright.getByText('Event saved',{exact:true}).first().waitFor({state:'visible',timeoutMs:15000});
      await exactSearch(a.marker,'created_lookup');
      const candidate=tab.playwright.getByRole('button').filter({hasText:a.marker});
      await candidate.waitFor({state:'visible',timeoutMs:15000});if(await candidate.count()!==1)throw Error('Saved marker is not unique');
      await action('open_created',{marker:a.marker},()=>candidate.click());await action('edit_created',{},()=>role('button','Edit event').click());
      row.native_id=await tab.url();await record('identity',{native_id:row.native_id});await checkpoint('created_identity');
      row.baseline=await reopen('baseline');if(row.baseline.x!==0||row.baseline.y!==0)throw Error('Baseline mismatch');
    });
  }
  async function seal(){row.seal={utc:now(),presented_later:[...row.assignment.presented_later],history_complete:row.assignment.history_complete,
    before_later:row.assignment.seal_before_later,verified_phase:row.later_phases.at(-1)?.observation.evidence_id??row.agent.evidence_id};
    const r=await record('history_seal',row.seal);row.seal.evidence_id=r.id;await checkpoint('seal');}
  async function inject(){return guarded('inject',async()=>{
    row.agent=await literal('agent',1,0,{expected:row.baseline});if(row.agent.x!==1||row.agent.y!==0)throw Error('Agent mismatch');await checkpoint('agent');
    if(row.assignment.seal_before_later)await seal();let v=row.agent;
    for(const command of row.assignment.full_later){const x=command==='add1'?v.x+1:command==='sub1'?v.x-1:command==='set0'?0:command==='set1'?1:v.x,y=command==='flip_y'?1-v.y:v.y;
      v=await literal('later_'+command,x,y,{expected:v});row.later_phases.push({command,observation:v});await checkpoint('later_'+command);if(v.x!==x||v.y!==y)throw Error('Later injection mismatch');}
    if(!row.assignment.seal_before_later)await seal();
  });}
  async function decideUndo(){return guarded('decide_undo',async()=>{
    row.preundo=await reopen('preundo');const expected=row.later_phases.at(-1)?.observation??row.agent;
    if(row.preundo.x!==expected.x||row.preundo.y!==expected.y)throw Error('Unexpected pre-undo saved change');
    row.prepare_input={initial:{x:row.baseline.x,y:row.baseline.y},agent:{x:row.agent.x,y:row.agent.y},current:{x:row.preundo.x,y:row.preundo.y,identity:row.preundo.identity,contract:row.preundo.contract,readId:row.preundo.readId,readAt:row.preundo.readAt,reloaded:row.preundo.reloaded},
      later:[...row.assignment.presented_later],historyComplete:row.assignment.history_complete,expectedIdentity:row.native_id};
    row.decision=prepare(row.assignment.rule,row.prepare_input);const e=await record('prepare',{input:row.prepare_input,output:row.decision});row.prepare_evidence_id=e.id;await checkpoint('prepared');
    if(row.decision.write){const requested={...row.decision.write},literalValue={...requested};if(row.assignment.fault==='x_plus_two')literalValue.x+=2;if(row.assignment.fault==='flip_y')literalValue.y=1-literalValue.y;
      row.actuator={requested,actual_literal:literalValue,fault:row.assignment.fault,attempted:true,utc:now()};const a=await record('actuator_instruction',row.actuator);row.actuator.evidence_id=a.id;row.write_attempts=1;await checkpoint('before_undo_attempt');
      row.actuator.saved=await literal('undo',literalValue.x,literalValue.y,{force:true,expected:row.preundo});await checkpoint('undo_saved');
      if(row.assignment.fault&&(row.actuator.saved.x!==literalValue.x||row.actuator.saved.y!==literalValue.y))throw Error('Deliberate actuator fault was not saved as prescribed');
    }else{row.actuator={attempted:false,requested:null,actual_literal:null,fault:row.assignment.fault};await record('no_undo_write',row.actuator);}
  });}
  async function verify(){return guarded('verify',async()=>{
    row.final_reads.push(await reopen('final_read_1'));await checkpoint('final_read_1');
    row.final_reads.push(await reopen('final_read_2'));await checkpoint('final_read_2');
    row.finish_input=row.final_reads.map(o=>({x:o.x,y:o.y,identity:o.identity,contract:o.contract,readId:o.readId,readAt:o.readAt,reloaded:o.reloaded}));row.finish=finish(row.assignment.rule,row.decision,row.finish_input);
    const e=await record('finish',{rule:row.assignment.rule,decision:row.decision,observations:row.finish_input,output:row.finish});row.finish_evidence_id=e.id;
    row.status='valid';await shot(row.trial_id+'_final');
  });}
  async function cleanup(){
    try{
      if(!row.native_id)throw Error('No known saved identity; inspect exact marker separately without another create');
      if(await tab.url()!==row.native_id)await reopen('cleanup_identity');
      await action('trash_menu',{},()=>role('button','More actions').click());await action('trash',{native_id:row.native_id,recoverable:true},()=>role('menuitem','Delete').click());
      await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});await tab.playwright.getByText('Event deleted',{exact:true}).first().waitFor({state:'visible',timeoutMs:15000});
      await exactSearch(row.assignment.marker,'cleanup_lookup');await action('cleanup_reload',{},()=>tab.reload());
      await tab.playwright.getByText('Loaded',{exact:true}).waitFor({state:'visible',timeoutMs:15000});
      await tab.playwright.getByText('No results found',{exact:true}).waitFor({state:'visible',timeoutMs:15000});await tab.playwright.getByRole('progressbar').waitFor({state:'hidden',timeoutMs:15000});
      const e=await obs('cleanup_ready_zero');if(e.state.includes('- progressbar')||e.state.includes('Searching')||!e.state.includes('- generic: No results found'))throw Error('Cleanup search is not ready');
      row.cleanup={status:'trashed',active_matches:0,evidence_ids:[e.id],native_id:row.native_id};await shot(row.trial_id+'_cleanup');
    }catch(e){row.cleanup={status:'unresolved',active_matches:null,reason:String(e),evidence_ids:[]};await record('cleanup_error',{error:String(e)});}
    row.ended_at=now();await checkpoint('terminal');await fs.appendFile(dir+'/trials.jsonl',JSON.stringify(row)+'\n');await record('trial_terminal',{trial_id:row.trial_id,status:row.status,finish:row.finish??null,cleanup:row.cleanup});
    console.log({trial_id:row.trial_id,status:row.status,finish:row.finish,cleanup:row.cleanup.status});return row;
  }
  return {begin,inject,decideUndo,verify,cleanup,record,obs,action,shot,fields,reopen,exactSearch,getState:()=>row};
}
