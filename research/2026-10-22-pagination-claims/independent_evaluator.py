"""Independent pagination rule oracle, from frozen plan only."""
from itertools import product

RULES=('empty_page','short_page','no_match_page','token_only','token_and_coverage','bounded_checked')
TYPES=((0,0),(0,1),(0,2),(1,0),(1,1),(2,0))
MODES=('complete','incomplete_zero_hidden','incomplete_one_hidden')


def evaluate(stream,mode,rule):
    assert 1 <= len(stream) <= 4
    assert all(tuple(x) in TYPES for x in stream)
    assert mode in MODES and rule in RULES
    stop=len(stream)
    if rule == 'bounded_checked':
        stop=min(stop,2)
    else:
        for position,(match,unrelated) in enumerate(stream,1):
            if (rule == 'empty_page' and match+unrelated == 0
                or rule == 'short_page' and match+unrelated < 2
                or rule == 'no_match_page' and match == 0):
                stop=position
                break
    full_chain=stop==len(stream)
    coverage=mode=='complete'
    claim=True if rule in RULES[:4] else full_chain and coverage
    seen=sum(x[0] for x in stream[:stop])
    truth=sum(x[0] for x in stream)+(mode=='incomplete_one_hidden')
    return {'pages_read':stop,'complete_claim':claim,'remaining_token':not full_chain,
      'seen_incomplete':not coverage,'returned_count':seen,'truth_count':truth,
      'unsupported_completion':claim and (not full_chain or not coverage),
      'incorrect_inventory':claim and seen != truth,'false_absence':claim and seen==0 and truth>0,
      'missing_matches':truth-seen,'unknown':not claim}


def corpus():
    for length in range(1,5):
        for stream in product(TYPES,repeat=length):
            for mode in MODES:
                for rule in RULES:
                    yield stream,mode,rule,evaluate(stream,mode,rule)
