#!/usr/bin/env python3
"""Focused safety and recovery checks for the reference decision function."""
import dataclasses
import itertools
import unittest
from v2_policy import Facts, decide


def complete(**updates):
    f = Facts(policy='Guard', baseline_verified_empty=True, create_admitted=1,
              observation_ready=True, observation_fresh=True, exact_title_count=1,
              native_id='id-1', detail_fresh=True, fields_match=True,
              scope_covered=True, coverage_fresh=True, operation_ids=('id-1',))
    return dataclasses.replace(f, **updates)


class PolicyTests(unittest.TestCase):
    def test_first_create_after_canceled_preparation(self):
        self.assertEqual(decide(Facts('Guard', baseline_verified_empty=True))['action'], 'create')

    def test_first_create_needs_empty_verified_baseline(self):
        self.assertEqual(decide(Facts('Guard'))['action'], 'read_scope')

    def test_title_repair_preserves_identity_action(self):
        f = complete(exact_title_count=0, fields_match=False, title_only_repair=True)
        self.assertEqual(decide(f)['action'], 'repair_same_id')

    def test_no_second_repair_when_wrong_title_remains(self):
        f = complete(exact_title_count=0, fields_match=False, title_only_repair=True, repair_admitted=True)
        self.assertEqual(decide(f)['action'], 'unresolved')

    def test_wrong_non_title_field_not_repaired_or_confirmed(self):
        self.assertEqual(decide(complete(fields_match=False))['action'], 'unresolved')

    def test_missing_identity_never_confirms(self):
        self.assertEqual(decide(complete(native_id=None))['action'], 'read_identity')

    def test_pending_edit_never_confirms(self):
        self.assertEqual(decide(complete(edit_pending=True))['action'], 'read_identity')

    def test_extra_partial_record_blocks_confirmation(self):
        self.assertEqual(decide(complete(operation_ids=('id-1', 'blank-id')))['action'], 'unresolved')

    def test_different_record_cannot_replace_first_identity(self):
        self.assertEqual(decide(complete(operation_ids=('id-2',)))['action'], 'unresolved')

    def test_missing_fields_never_confirm(self):
        self.assertEqual(decide(complete(fields_match=None))['action'], 'read_identity')

    def test_missing_coverage_never_confirms(self):
        for changes in ({'scope_covered': False}, {'coverage_fresh': False}, {'operation_ids': None}):
            with self.subTest(changes=changes):
                self.assertEqual(decide(complete(**changes))['action'], 'read_scope')

    def test_unready_or_stale_positive_is_unknown(self):
        for changes in ({'observation_ready': False}, {'observation_fresh': False}, {'exact_title_count': None}):
            with self.subTest(changes=changes):
                self.assertEqual(decide(complete(**changes))['action'], 'read_scope')

    def test_clean_confirmation(self):
        self.assertEqual(decide(complete())['action'], 'confirm')

    def test_deadline_prevents_any_new_action_or_confirmation(self):
        for creates in range(3):
            self.assertEqual(decide(complete(create_admitted=creates, deadline_expired=True))['action'], 'unresolved')

    def test_baseline_reproduces_blank_row_failure_gate(self):
        blank = complete(policy='Absence', exact_title_count=0, fields_match=False,
                         operation_ids=('blank-id',), native_id='blank-id')
        self.assertEqual(decide(blank)['action'], 'create')
        after_repeat = dataclasses.replace(blank, create_admitted=2, exact_title_count=1,
                                          operation_ids=('blank-id', 'new-id'))
        self.assertEqual(decide(after_repeat)['action'], 'confirm')

    def test_baseline_has_only_one_repeat(self):
        self.assertEqual(decide(complete(policy='Absence', create_admitted=2, exact_title_count=0))['action'], 'unresolved')

    def test_guard_no_recreate_in_2304_pending_combinations(self):
        count = 0
        for creates, ready, fresh, title_count, ident, detail, fields, covered, pending in itertools.product(
                (1, 2, 3), (False, True), (False, True), (None, 0, 1, 2),
                (None, 'id-1'), (False, True), (None, False, True), (False, True), (False, True)):
            f = complete(create_admitted=creates, observation_ready=ready, observation_fresh=fresh,
                         exact_title_count=title_count, native_id=ident, detail_fresh=detail,
                         fields_match=fields, scope_covered=covered, edit_pending=pending)
            self.assertNotEqual(decide(f)['action'], 'create')
            count += 1
        self.assertEqual(count, 2304)

    def test_invalid_evidence_types_rejected(self):
        for changes in ({'observation_ready': 'false'}, {'fields_match': 1}, {'native_id': ''},
                        {'scope_covered': 1}, {'edit_pending': None}, {'policy': []}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                decide(complete(**changes))

    def test_invalid_counts_rejected(self):
        for f in (complete(create_admitted=-1), complete(exact_title_count=-1), complete(create_admitted=True)):
            with self.assertRaises(ValueError):
                decide(f)


if __name__ == '__main__':
    unittest.main(verbosity=2)
