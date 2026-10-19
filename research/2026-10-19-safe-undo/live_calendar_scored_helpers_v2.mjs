// Executed browser helper. Uses only supported visible UI actions and reads.
export function createRunner({tab, fs, dir, decide, record, act, obs, shot, setContext}) {
  const role=(r,n)=>tab.playwright.getByRole(r,{name:n,exact:true});
  let current=null;
  async function ready() { await role('textbox','Description').waitFor({state:'visible',timeoutMs:15000}); }
  async function fields(label) {
    await ready(); const dom=await obs(label+'_dom',false);
    const raw={url:await tab.url(),title:await role('textbox','Title').getAttribute('value'),
      x_raw:await role('textbox','Description').innerText(),y_raw:await role('combobox','Show as').innerText(),
      start:await role('textbox','Start date').getAttribute('value'),end:await role('textbox','End date').getAttribute('value'),
      all_day:await role('checkbox','All day').getAttribute('aria-checked'),
      visibility:await role('combobox','Visibility').innerText(),recurrence:await role('combobox','Recurrence').innerText(),
      guests:await role('combobox','Guests').getAttribute('value'),guest_panel:await role('tabpanel','Guests').innerText(),
      notifications:await role('list','Notifications').innerText(),location:await role('combobox','Add location').getAttribute('value'),
      conference_absent:await role('button','Add Google Meet video conferencing').count()===1};
    const norm=raw.x_raw.replace(/^[\r\n]+|[\r\n]+$/g,'');
    const checks={dates:raw.start==='Oct 14, 2026'&&raw.end==='Oct 14, 2026',all_day:raw.all_day==='true',
      private:raw.visibility==='Private',recurrence:raw.recurrence==='Does not repeat',
      guests:(raw.guests===null||raw.guests==='')&&raw.guest_panel.trim()==='Guest permissions\nModify event\nInvite others\nSee guest list',
      notifications:raw.notifications==='',location:raw.location===null||raw.location==='',conference:raw.conference_absent};
    const v={x:/^-?\d+$/.test(norm)?Number(norm):null,y:raw.y_raw==='Free'?0:raw.y_raw==='Busy'?1:null,
      x_raw:raw.x_raw,y_raw:raw.y_raw,native_id:raw.url,token:current.token,
      identity_ok:raw.title===current.token&&(!current.native_id||raw.url===current.native_id),
      contract_ok:Object.values(checks).every(Boolean),reloaded:true,utc:new Date().toISOString(),checks,raw};
    const ev=await record('saved_fields',{label,...v,source_observation:dom.id});v.evidence_id=ev.id;
    if(!v.identity_ok||!v.contract_ok||v.x===null||v.y===null)throw Error('Saved field contract failed: '+JSON.stringify(v));
    return v;
  }
  async function reopen(label) {
    if(await tab.url()===current.native_id)await act(label+'_reload',{},()=>tab.reload());
    else await act(label+'_open',{url:current.native_id},()=>tab.goto(current.native_id));
    await ready();return fields(label);
  }
  async function save(label) {
    await act(label+'_save',{},()=>role('button','Save').click());
    await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});
    await tab.playwright.getByText('Event saved',{exact:true}).waitFor({state:'visible',timeoutMs:15000});
    await obs(label+'_saved_notice',false);
    return reopen(label+'_saved');
  }
  async function setLiteral(label,x,y) {
    const before=await fields(label+'_before');
    if(before.x!==x)await act(label+'_set_x',{value:String(x)},()=>role('textbox','Description').fill(String(x)));
    if(before.y!==y){await act(label+'_show_as',{},()=>role('combobox','Show as').click());
      await act(label+'_set_y',{value:y?'Busy':'Free'},()=>role('option',y?'Busy':'Free').click());}
    if(before.x===x&&before.y===y)return reopen(label+'_no_op');
    return save(label);
  }
  async function search(token,label) {
    if(await role('combobox','Search').count()===0)await act(label+'_open_search',{},()=>role('button','Search').click());
    await act(label+'_query',{token},async()=>{await role('combobox','Search').fill(token);await role('combobox','Search').press('Enter');});
    await role('combobox','Search').waitFor({state:'visible',timeoutMs:15000});
    return obs(label+'_results',false);
  }
  async function create(a) {
    if(!await role('button','Create').isEnabled())await act('leave_search',{},()=>role('button','Go back').click());
    await act('create_menu',{},()=>role('button','Create').click());
    await act('create_event',{},()=>role('menuitem','Event').click());
    await act('full_editor',{},()=>role('button','More options').click());
    await act('title',{value:a.token},()=>role('textbox','Title').fill(a.token));
    await act('all_day',{value:true},()=>role('checkbox','All day').check());
    for(const name of ['Start date','End date'])await act('set_'+name,{value:'Oct 14, 2026'},async()=>{await role('textbox',name).fill('Oct 14, 2026');await role('textbox',name).press('Tab');});
    await act('baseline_x',{value:'0'},()=>role('textbox','Description').fill('0'));
    const reminders=await role('button','Remove notification').count();
    for(let i=0;i<reminders;i++)await act('remove_notification',{index:i},()=>role('button','Remove notification').first().click());
    await act('visibility_menu',{},()=>role('combobox','Visibility').click());
    await act('private',{value:'Private'},()=>role('option','Private').click());
    await act('create_save',{},()=>role('button','Save').click());
    await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});
    await tab.playwright.getByText('Event saved',{exact:true}).waitFor({state:'visible',timeoutMs:15000});
    await search(a.token,'created_lookup');
    const bn='All day, '+a.token+', <ACCOUNT_DISPLAY_NAME>, No location, October 14, 2026';
    await role('button',bn).waitFor({state:'visible',timeoutMs:15000});
    await act('created_detail',{title:a.token},()=>role('button',bn).click());
    await act('created_edit',{},()=>role('button','Edit event').click());
    current.native_id=await tab.url();await record('identity',{native_id:current.native_id,token:a.token});
    return reopen('baseline');
  }
  async function cleanup() {
    if(!current.native_id)return {status:'unresolved',active_matches:null,evidence_ids:[]};
    if(await tab.url()!==current.native_id)await reopen('cleanup_identity');
    await act('cleanup_menu',{},()=>role('button','More actions').click());
    await act('cleanup_trash',{recoverable:true,native_id:current.native_id},()=>role('menuitem','Delete').click());
    await role('textbox','Title').waitFor({state:'hidden',timeoutMs:15000});
    await tab.playwright.getByText('Event deleted',{exact:true}).waitFor({state:'visible',timeoutMs:15000});
    await search(current.token,'cleanup_search');
    await role('heading','Search results. No events found.').waitFor({state:'visible',timeoutMs:15000});
    const ev=await obs('cleanup_active_zero',false);await shot(current.trial_id+'_cleanup');
    return {status:'trashed',active_matches:0,evidence_ids:[ev.id],native_id:current.native_id};
  }
  async function run(a) {
    current={...a,started_at:new Date().toISOString(),native_id:null,terminal_status:'unknown',reason:null,later:[],decision:null};
    setContext(a);await record('trial_start',{assignment:a});
    try {
      current.baseline=await create(a);if(current.baseline.x!==0||current.baseline.y!==0)throw Error('Baseline injection mismatch');
      current.agent=await setLiteral('agent',1,0);if(current.agent.x!==1||current.agent.y!==0)throw Error('Agent injection mismatch');
      let value=current.agent;
      for(const command of a.later) {
        const x=command==='add1'?value.x+1:command==='sub1'?value.x-1:command==='set0'?0:command==='set1'?1:value.x;
        const y=command==='flip_y'?1-value.y:value.y;
        value=await setLiteral('later_'+command,x,y);current.later.push({command,observation:value});
        if(value.x!==x||value.y!==y)throw Error('Later injection mismatch');
      }
      current.preundo=await reopen('preundo');
      if(a.kind==='core'){
        current.decision=decide(a.rule,{x:current.preundo.x,y:current.preundo.y},current.later.map(z=>z.command));
        const ev=await record('rule_decision',{rule:a.rule,input:{x:current.preundo.x,y:current.preundo.y},later:current.later.map(z=>z.command),output:current.decision});
        current.decision_evidence_id=ev.id;
        current.final=current.decision.status==='abstain'?await reopen('final_abstain'):await setLiteral('undo',current.decision.x,current.decision.y);
      }else current.final=await reopen('diagnostic_final');
      await shot(a.trial_id+'_final');current.terminal_status='valid';
    }catch(e){current.reason=String(e);await record('trial_error',{error:String(e)});}
    try{current.cleanup=await cleanup();}catch(e){current.cleanup={status:'unresolved',active_matches:null,evidence_ids:[],reason:String(e)};await record('cleanup_error',{error:String(e)});}
    current.ended_at=new Date().toISOString();await fs.appendFile(dir+'/trials.jsonl',JSON.stringify(current)+'\n');
    await record('trial_end',{trial_id:a.trial_id,terminal_status:current.terminal_status,cleanup:current.cleanup});
    console.log({trial_id:a.trial_id,status:current.terminal_status,reason:current.reason,final:current.final&&[current.final.x,current.final.y],decision:current.decision,cleanup:current.cleanup.status});
    return current;
  }
  return {run,fields,reopen,search};
}
