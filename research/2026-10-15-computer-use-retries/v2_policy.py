#!/usr/bin/env python3
"""Reference policy over facts validated from saved evidence. Not a browser driver."""
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Facts:
    policy: str
    deadline_expired: bool = False
    baseline_verified_empty: bool = False
    create_admitted: int = 0
    observation_ready: bool = False
    observation_fresh: bool = False
    exact_title_count: Optional[int] = None
    native_id: Optional[str] = None
    detail_fresh: bool = False
    fields_match: Optional[bool] = None
    title_only_repair: bool = False
    repair_admitted: bool = False
    edit_pending: bool = False
    scope_covered: bool = False
    coverage_fresh: bool = False
    operation_ids: Optional[Tuple[str, ...]] = None


def decide(f: Facts) -> dict:
    """Return an action and its reason. Missing facts do not become positive proof.

    create_admitted counts potentially effective Create requests reserved before
    execution, including requests with uncertain responses. Do not reset it on
    an empty read or timeout. Fresh means a completed reload after the last
    mutation. Native identity and operation ownership must be checked outside
    this function. An operation_ids tuple must be the complete covered set.
    """
    if not isinstance(f.policy, str) or f.policy not in {'Absence', 'Guard'}:
        raise ValueError('Unknown policy')
    bool_fields = ('deadline_expired', 'baseline_verified_empty', 'observation_ready',
                   'observation_fresh', 'detail_fresh', 'title_only_repair',
                   'repair_admitted', 'edit_pending', 'scope_covered', 'coverage_fresh')
    if any(type(getattr(f, key)) is not bool for key in bool_fields):
        raise ValueError('Invalid boolean evidence flag')
    if f.fields_match is not None and type(f.fields_match) is not bool:
        raise ValueError('Invalid field status')
    if f.native_id is not None and (not isinstance(f.native_id, str) or not f.native_id.strip()):
        raise ValueError('Invalid native identity')
    if not isinstance(f.create_admitted, int) or isinstance(f.create_admitted, bool) or f.create_admitted < 0:
        raise ValueError('Invalid create count')
    if f.exact_title_count is not None and (not isinstance(f.exact_title_count, int) or isinstance(f.exact_title_count, bool) or f.exact_title_count < 0):
        raise ValueError('Invalid exact-title count')
    if f.operation_ids is not None and (not isinstance(f.operation_ids, tuple) or any(not isinstance(x, str) or not x for x in f.operation_ids)):
        raise ValueError('Invalid operation identity set')
    def result(action, reason):
        return {'action': action, 'reason': reason}
    if f.deadline_expired:
        return result('unresolved', 'decision_deadline')
    if f.create_admitted == 0:
        if f.baseline_verified_empty and not f.edit_pending and f.native_id is None:
            return result('create', 'first_effective_create')
        return result('read_scope', 'verify_empty_baseline_or_existing_effect')
    if not f.observation_ready or not f.observation_fresh or f.exact_title_count is None:
        return result('read_scope', 'observation_unknown')
    if f.policy == 'Absence':
        if f.create_admitted > 2:
            return result('unresolved', 'create_budget_violation')
        if f.exact_title_count == 1:
            return result('confirm', 'baseline_exact_title_one')
        if f.exact_title_count > 1:
            return result('unresolved', 'multiple_exact_titles')
        if f.create_admitted == 1:
            return result('create', 'baseline_zero_permits_one_repeat')
        return result('unresolved', 'baseline_repeat_used')
    if f.create_admitted != 1:
        return result('unresolved', 'guard_create_budget_violation')
    if f.native_id is None:
        return result('read_identity', 'identity_unknown_no_new_create')
    if f.edit_pending:
        return result('read_identity', 'edit_outcome_pending')
    if not f.detail_fresh or f.fields_match is None:
        return result('read_identity', 'stored_fields_unknown')
    if not f.fields_match:
        if f.title_only_repair and not f.repair_admitted:
            return result('repair_same_id', 'repair_title_on_first_record')
        return result('unresolved', 'wrong_fields_or_repair_budget_used')
    if not f.scope_covered or not f.coverage_fresh or f.operation_ids is None:
        return result('read_scope', 'cover_all_operation_records')
    if set(f.operation_ids) != {f.native_id}:
        return result('unresolved', 'covered_identity_set_mismatch')
    if f.exact_title_count != 1:
        return result('unresolved', 'covered_exact_title_count_mismatch')
    return result('confirm', 'one_known_record_correct_fields_covered')


if __name__ == '__main__':
    import json
    import sys
    raw = json.load(sys.stdin)
    if raw.get('operation_ids') is not None:
        raw['operation_ids'] = tuple(raw['operation_ids'])
    print(json.dumps(decide(Facts(**raw)), sort_keys=True))
