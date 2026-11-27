# Requirements

<!-- The behavior a user can observe, each with a stable number and the check that proves it, next to the behavior it describes. -->

| ID  | Requirement | Check |
| --- | ----------- | ----- |

| CP-1 | Admission inspects every reachable parent, including both parents of a merge, and rejects an incorrect author or committer. | test/credit-protection.test.js; CreditProtectionTests.test_cp1_inspects_both_merge_parents_and_rejects_wrong_identity |
| CP-2 | New commit objects require exactly one nonempty Why, How and Tags section, with same-line or following-line values. Only exact repository-bound reviewed historical objects retain their formatting. Every message still passes project credit-field and prohibited-credit checks; all ancestors retain identity and object validation. | test/credit-protection.test.js; CreditProtectionTests.test_cp2_requires_nonempty_sections_and_rejects_credit_trailers; ProspectiveFormatTests |
| CP-3 | A branch update requires the recorded predecessor in candidate ancestry; branch creation has no predecessor. | test/credit-protection.test.js; CreditProtectionTests.test_cp3_requires_predecessor_before_update |
| CP-4 | Invalid destination, repository identifier or head bindings stop before object reads. | test/credit-protection.test.js; CreditProtectionTests.test_cp4_rejects_binding_drift_before_object_reads |
