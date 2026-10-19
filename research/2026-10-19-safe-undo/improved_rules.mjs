// Fixed experimental controller. No evaluator target is an input.
const commands = new Set(['add1','sub1','set0','set1','flip_y']);
const fields = s => s && Number.isSafeInteger(s.x) && [0,1].includes(s.y);
const equal = (a,b) => fields(a) && fields(b) && a.x===b.x && a.y===b.y;
export function replay(start, later) {
  if (!fields(start) || !Array.isArray(later) || later.some(c=>!commands.has(c))) throw new Error('Invalid command record');
  const state={x:start.x,y:start.y};
  for(const command of later){
    if(command==='add1')state.x++;
    if(command==='sub1')state.x--;
    if(command==='set0')state.x=0;
    if(command==='set1')state.x=1;
    if(command==='flip_y')state.y=1-state.y;
    if(!Number.isSafeInteger(state.x))throw new Error('Integer range exceeded');
  }
  return state;
}
export function prepare(rule,input){
  const {initial,agent,current,later,historyComplete,expectedIdentity}=input;
  if(!fields(current)||!Array.isArray(later)||later.some(c=>!commands.has(c)))return {status:'abstain',reason:'invalid_input',write:null,target:null};
  if(rule==='baseline_log_provenance'){
    const target={x:later.some(c=>c==='set0'||c==='set1')?current.x:current.x-1,y:current.y};
    return {status:'complete',reason:'legacy_decision',write:equal(current,target)?null:target,target};
  }
  if(rule!=='checked_history')throw new Error('Unknown rule');
  const refuse=reason=>({status:'abstain',reason,write:null,target:null});
  if(!fields(initial)||!fields(agent)||!expectedIdentity||current.identity!==expectedIdentity||current.contract!==true)return refuse('identity_or_contract');
  if(current.reloaded!==true||typeof current.readId!=='string'||!current.readId||!Number.isFinite(Date.parse(current.readAt)))return refuse('missing_fresh_preread');
  if(agent.x!==initial.x+1||agent.y!==initial.y)return refuse('agent_record');
  if(historyComplete!==true)return refuse('incomplete_history');
  const expected=replay(agent,later);
  if(!equal(current,expected))return refuse('prestate_mismatch');
  const target=replay(initial,later);
  return {status:'pending',reason:'verify_saved_target',write:equal(current,target)?null:target,target,expectedIdentity,preReadId:current.readId,preReadAt:current.readAt};
}
export function finish(rule,decision,observations){
  if(rule==='baseline_log_provenance')return {status:decision.status,reason:decision.reason};
  if(rule!=='checked_history')throw new Error('Unknown rule');
  if(decision.status==='abstain')return {status:'abstain',reason:decision.reason};
  if(!Array.isArray(observations)||observations.length!==2)return {status:'unknown',reason:'missing_saved_reads'};
  if(observations.some(o=>!o||o.identity!==decision.expectedIdentity||o.contract!==true||!fields(o)))return {status:'unknown',reason:'saved_identity_or_contract'};
  if(observations.some(o=>o.reloaded!==true||typeof o.readId!=='string'||!o.readId||!Number.isFinite(Date.parse(o.readAt)))||observations[0].readId===observations[1].readId||observations.some(o=>o.readId===decision.preReadId)||Date.parse(observations[0].readAt)<=Date.parse(decision.preReadAt)||Date.parse(observations[1].readAt)<=Date.parse(observations[0].readAt))return {status:'unknown',reason:'saved_read_freshness'};
  if(observations.some(o=>!equal(o,decision.target)))return {status:'abstain',reason:'saved_target_mismatch'};
  return {status:'complete',reason:'two_saved_target_matches'};
}
