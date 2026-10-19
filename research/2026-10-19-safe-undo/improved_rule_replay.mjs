import {readFileSync,writeFileSync} from 'node:fs';
import {prepare,finish} from './improved_rules.mjs';
import assert from 'node:assert/strict';
const packageDir=process.argv[2]||'.';
const rows=readFileSync(packageDir+'/improved_trials.jsonl','utf8').trim().split('\n').map(JSON.parse);
const checked=[];
for(const row of rows){
 if(!row.prepare_input||!row.decision)continue;
 const d=prepare(row.assignment.rule,row.prepare_input);assert.deepEqual(d,row.decision,'prepare '+row.trial_id);
 if(row.finish&&row.finish_input){const result=finish(row.assignment.rule,d,row.finish_input);assert.deepEqual(result,row.finish,'finish '+row.trial_id);checked.push(row.trial_id);}
}
const result={status:'PASS',assignments:rows.length,complete_decision_replays:checked.length,checked};
writeFileSync(process.argv[3]||'improved_rule_replay.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
