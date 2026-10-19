import assert from 'node:assert/strict';
import {prepare,finish,replay} from './improved_rules.mjs';
import {writeFileSync} from 'node:fs';
const checks=[];
function test(name,fn){fn();checks.push(name);}
let sequence=0;
const obs=(x,y,extra={})=>({x,y,identity:'temporary-record',contract:true,reloaded:true,readId:'read-'+(++sequence),readAt:new Date(1792425600000+sequence*1000).toISOString(),...extra});
const input=(later=[],extra={})=>({initial:{x:0,y:0},agent:{x:1,y:0},current:obs(replay({x:1,y:0},later).x,replay({x:1,y:0},later).y),later,historyComplete:true,expectedIdentity:'temporary-record',...extra});
for(const later of [[],['flip_y'],['add1'],['set0','set1'],['sub1']]){
 test('complete supported history '+JSON.stringify(later),()=>{const d=prepare('checked_history',input(later));assert.equal(d.status,'pending');const t=replay({x:0,y:0},later);assert.deepEqual(d.target,t);assert.equal(finish('checked_history',d,[obs(t.x,t.y),obs(t.x,t.y)]).status,'complete');});
}
test('known incomplete history refuses',()=>assert.equal(prepare('checked_history',input([],{historyComplete:false})).reason,'incomplete_history'));
test('changed prestate refuses',()=>assert.equal(prepare('checked_history',input([],{current:obs(2,0)})).reason,'prestate_mismatch'));
test('wrong record refuses',()=>assert.equal(prepare('checked_history',input([],{current:obs(1,0,{identity:'other-record'})})).reason,'identity_or_contract'));
test('invalid contract refuses',()=>assert.equal(prepare('checked_history',input([],{current:obs(1,0,{contract:false})})).reason,'identity_or_contract'));
test('invalid agent action refuses',()=>assert.equal(prepare('checked_history',input([],{agent:{x:2,y:0}})).reason,'agent_record'));
test('unknown command refuses',()=>assert.equal(prepare('checked_history',input([],{later:['unknown']})).reason,'invalid_input'));
test('non-integer refuses',()=>assert.equal(prepare('checked_history',input([],{current:obs('1',0)})).reason,'invalid_input'));
const d=prepare('checked_history',input());
test('wrong X blocks completion',()=>assert.equal(finish('checked_history',d,[obs(1,0),obs(1,0)]).reason,'saved_target_mismatch'));
test('wrong Y blocks completion',()=>assert.equal(finish('checked_history',d,[obs(0,1),obs(0,1)]).reason,'saved_target_mismatch'));
test('first good second wrong blocks completion',()=>assert.equal(finish('checked_history',d,[obs(0,0),obs(1,0)]).reason,'saved_target_mismatch'));
test('only one read unknown',()=>assert.equal(finish('checked_history',d,[obs(0,0)]).status,'unknown'));
test('wrong saved identity unknown',()=>assert.equal(finish('checked_history',d,[obs(0,0),obs(0,0,{identity:'other'})]).status,'unknown'));
test('invalid saved contract unknown',()=>assert.equal(finish('checked_history',d,[obs(0,0),obs(0,0,{contract:false})]).status,'unknown'));
test('refusal remains refusal',()=>assert.equal(finish('checked_history',prepare('checked_history',input([],{historyComplete:false})),[]).status,'abstain'));
test('legacy claim does not inspect poststate',()=>assert.equal(finish('baseline_log_provenance',prepare('baseline_log_provenance',input()),[obs(1,0),obs(1,0)]).status,'complete'));
test('duplicate final read unknown',()=>{const o=obs(0,0);assert.equal(finish('checked_history',d,[o,o]).reason,'saved_read_freshness');});
test('missing reload unknown',()=>assert.equal(finish('checked_history',d,[obs(0,0),obs(0,0,{reloaded:false})]).reason,'saved_read_freshness'));
test('pre-read reused unknown',()=>assert.equal(finish('checked_history',d,[obs(0,0,{readId:d.preReadId}),obs(0,0)]).reason,'saved_read_freshness'));
test('out of order time unknown',()=>{const a=obs(0,0),b=obs(0,0);assert.equal(finish('checked_history',d,[b,a]).reason,'saved_read_freshness');});
const limitation={description:'A falsely complete empty log hides set0,set1. Equal current fields do not detect the omitted commands.',full_later:['set0','set1'],presented_later:[],true_target:replay({x:0,y:0},['set0','set1']),decision:d,finish:finish('checked_history',d,[obs(0,0),obs(0,0)])};
test('dishonest-history limit remains observable',()=>{assert.equal(limitation.finish.status,'complete');assert.notDeepEqual(limitation.true_target,d.target);});
const result={status:'PASS',checks:checks.length,names:checks,trust_limit:limitation};
writeFileSync(process.argv[2]||'improved_rule_checks.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({status:result.status,checks:result.checks,trust_limit:'retained'}));
