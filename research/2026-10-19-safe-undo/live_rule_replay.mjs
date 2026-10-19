// Recompute the actual frozen JavaScript rule output for saved valid trials.
import {readFileSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {decide} from './live_rules.js';
const base=process.argv[2]??'.';
const output=process.argv[3]??base;
const trials=readFileSync(join(base,'live_trials.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const checks=[];
for(const t of trials){
  if(t.terminal_status!=='valid'||t.kind!=='core')continue;
  const actual=decide(t.rule,{x:t.preundo.x,y:t.preundo.y},t.later.map(v=>v.command));
  const matched=['status','x','y'].every(k=>actual[k]===t.decision[k]);
  checks.push({trial_id:t.trial_id,matched});
  if(!matched)throw Error('Decision differs from frozen rule: '+t.trial_id);
}
const result={status:'PASS',node:process.version,valid_decisions_checked:checks.length,checks};
writeFileSync(join(output,'live_rule_replay.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,valid_decisions_checked:checks.length}));
