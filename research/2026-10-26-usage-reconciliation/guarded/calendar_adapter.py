#!/usr/bin/env python3
"""Build a Calendar proof only after both connector and exact-record zone checks."""
import hashlib,json
from datetime import datetime

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def sha(x):return hashlib.sha256(canon(x).encode()).hexdigest()
def instant(x):return datetime.fromisoformat(x.replace('Z','+00:00'))

def make_proof(payload,observation,zone,record_alias,permit_hash):
    """Inputs are safe extracts. Their link to the private exact ID needs an audit."""
    if sha(payload)!=permit_hash:raise ValueError('payload_hash_mismatch')
    if observation.get('record_alias')!=record_alias:raise ValueError('wrong_observation_record')
    fields=observation['fields']
    required={k:payload[k] for k in ('summary','start','end','visibility','transparency','attendees','reminders','recurrence','hangout_link')}
    if not all(k in fields for k in (*required,'status')):raise ValueError('missing_returned_field')
    if any(fields.get(k)!=v for k,v in required.items()):raise ValueError('returned_field_mismatch')
    if fields.get('status')!='confirmed':raise ValueError('record_not_confirmed')
    if not zone or zone.get('alias')!=record_alias:raise ValueError('missing_exact_record_timezone')
    if zone.get('verified') is not True or zone.get('expected_timezone')!=payload['timezone']:
        raise ValueError('timezone_not_verified')
    if not zone.get('observed_label') or not zone.get('evidence_sha256'):
        raise ValueError('missing_timezone_evidence')
    if payload['timezone']!='America/Toronto' or not zone['observed_label'].endswith('Eastern Time - Toronto') or zone.get('end_observed_label')!=zone['observed_label']:
        raise ValueError('timezone_label_mismatch')
    hashes=observation['evidence_sha256']+zone['evidence_sha256']
    if not hashes or any(len(h)!=64 or any(c not in '0123456789abcdef' for c in h) for h in hashes):
        raise ValueError('invalid_evidence_hash')
    observed_at=max((observation['observed_at'],zone['observed_at']),key=instant)
    return {'status':'saved','observed_at':observed_at,'record_alias':record_alias,'fields_verified':True,
            'payload_sha256':permit_hash,'evidence_sha256':hashes}

# The zone observation remains trusted input. This module does not authenticate
# a website, infer an IANA zone from a UTC offset, or replace exact-ID UI checks.
