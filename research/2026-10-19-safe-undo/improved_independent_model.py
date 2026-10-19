"""Separate model for the frozen improved-undo study. Standard library only.

The reviewer inspected the controller for design review. This implementation
uses the written plan and does not import that controller or the main analyzer.
"""
from datetime import datetime

MAX_INT = 2**53-1
COMMANDS = {'add1','sub1','set0','set1','flip_y'}


def fields(v):
    return isinstance(v,dict) and type(v.get('x')) is int and abs(v['x'])<=MAX_INT and type(v.get('y')) is int and v['y'] in (0,1)

def vector(v):
    if not fields(v):raise ValueError('Invalid field vector')
    return v['x'],v['y']

def moment(t):
    if not isinstance(t,str):raise ValueError('Time must be a string')
    v=datetime.fromisoformat(t.replace('Z','+00:00'))
    if v.tzinfo is None:raise ValueError('Time lacks timezone')
    return v

def has_time(t):
    try:moment(t);return True
    except (TypeError,ValueError):return False

def replay(start, commands):
    x,y=vector(start)
    if not isinstance(commands,list):raise ValueError('Command list missing')
    states=[]
    for c in commands:
        if c not in COMMANDS:raise ValueError('Unknown command')
        if c=='add1':x+=1
        elif c=='sub1':x-=1
        elif c=='set0':x=0
        elif c=='set1':x=1
        else:y=1-y
        if abs(x)>MAX_INT:raise ValueError('Unsafe integer')
        states.append({'x':x,'y':y})
    return {'x':x,'y':y},states

def refusal(reason):return {'status':'abstain','reason':reason,'write':None,'target':None}

def prepare(rule, data):
    now=data.get('current');commands=data.get('later')
    if not fields(now) or not isinstance(commands,list) or any(c not in COMMANDS for c in commands):return refusal('invalid_input')
    if rule=='baseline_log_provenance':
        x,y=vector(now)
        target={'x':x if any(c in ('set0','set1') for c in commands) else x-1,'y':y}
        return {'status':'complete','reason':'legacy_decision','write':None if target=={'x':x,'y':y} else target,'target':target}
    if rule!='checked_history':raise ValueError('Unknown rule')
    initial=data.get('initial');agent=data.get('agent');identity=data.get('expectedIdentity')
    if not fields(initial) or not fields(agent) or not identity or now.get('identity')!=identity or now.get('contract') is not True:return refusal('identity_or_contract')
    if now.get('reloaded') is not True or not isinstance(now.get('readId'),str) or not now['readId'] or not has_time(now.get('readAt')):return refusal('missing_fresh_preread')
    if vector(agent)!=(initial['x']+1,initial['y']):return refusal('agent_record')
    if data.get('historyComplete') is not True:return refusal('incomplete_history')
    expected,_=replay(agent,commands)
    if vector(now)!=vector(expected):return refusal('prestate_mismatch')
    candidate,_=replay(initial,commands)
    return {'status':'pending','reason':'verify_saved_target','target':candidate,'write':None if vector(now)==vector(candidate) else candidate,'expectedIdentity':identity,'preReadId':now['readId'],'preReadAt':now['readAt']}

def finish(rule, decision, reads):
    if rule=='baseline_log_provenance':return {'status':decision['status'],'reason':decision['reason']}
    if rule!='checked_history':raise ValueError('Unknown rule')
    if decision['status']=='abstain':return {'status':'abstain','reason':decision['reason']}
    if not isinstance(reads,list) or len(reads)!=2:return {'status':'unknown','reason':'missing_saved_reads'}
    if any(not fields(r) or r.get('contract') is not True or r.get('identity')!=decision.get('expectedIdentity') for r in reads):return {'status':'unknown','reason':'saved_identity_or_contract'}
    ids=[r.get('readId') for r in reads]
    fresh=all(r.get('reloaded') is True and isinstance(r.get('readId'),str) and r['readId'] and has_time(r.get('readAt')) for r in reads)
    fresh=fresh and ids[0]!=ids[1] and decision.get('preReadId') not in ids
    fresh=fresh and moment(decision['preReadAt'])<moment(reads[0]['readAt'])<moment(reads[1]['readAt'])
    if not fresh:return {'status':'unknown','reason':'saved_read_freshness'}
    if any(vector(r)!=vector(decision['target']) for r in reads):return {'status':'abstain','reason':'saved_target_mismatch'}
    return {'status':'complete','reason':'two_saved_target_matches'}

def grade(status, reads, target):
    if status=='unknown':return 'unknown'
    if status not in ('complete','abstain'):raise ValueError('Unknown final controller status')
    if len(reads)!=2 or not all(fields(r) for r in reads):return 'unsupported_complete' if status=='complete' else 'unknown'
    correct=all(vector(r)==vector(target) for r in reads)
    if status=='complete':return 'clean_completion' if correct else 'false_confirmation'
    return 'abstain_correct' if correct else 'unresolved'
