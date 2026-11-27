import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import publication_adapter
from production_policy import issuer, policy


class GraphSource:
    def __init__(self, graph):
        self.graph = graph
        self.reads = []

    def commit_json(self, sha):
        self.reads.append(sha)
        return self.graph[sha]


def entry(parents=(), author=None, committer=None, message=None):
    name, email = policy.REQUIRED_IDENT
    return {
        "parents": [{"sha": parent} for parent in parents],
        "author": author or {"name": name, "email": email},
        "committer": committer or {"name": name, "email": email},
        "message": message
        or "Check publication\n\nWhy: Check identity.\nHow: Inspect parents.\nTags: Enhancement\n",
    }


class CreditProtectionTests(unittest.TestCase):
    def test_cp1_inspects_both_merge_parents_and_rejects_wrong_identity(self):
        head, left, right = "1" * 40, "2" * 40, "3" * 40
        for role in ("author", "committer"):
            with self.subTest(role=role):
                graph = {
                    head: entry((left, right)),
                    left: entry(),
                    right: entry(
                        **{role: {"name": "Other", "email": "other@example.invalid"}}
                    ),
                }
                source = GraphSource(graph)
                with self.assertRaises(issuer.Refusal):
                    issuer.admit(source, head)
                self.assertIn(right, source.reads)
        source = GraphSource(
            {head: entry((left, right)), left: entry(), right: entry()}
        )
        self.assertEqual(set(issuer.admit(source, head)), {head, left, right})

    def test_cp2_requires_nonempty_sections_and_rejects_credit_trailers(self):
        valid = entry()["message"]
        policy.check_message(valid)
        for section in policy.REQUIRED_SECTIONS:
            with self.subTest(section=section):
                lines = [
                    line for line in valid.splitlines() if not line.startswith(section)
                ]
                with self.assertRaises(ValueError):
                    policy.check_message("\n".join(lines))
                lines.append(section)
                with self.assertRaises(ValueError):
                    policy.check_message("\n".join(lines))
        with self.assertRaises(ValueError):
            policy.check_message(
                valid + "Co-authored-by: Other <other@example.invalid>\n"
            )

    def test_cp3_requires_predecessor_before_update(self):
        issuer.require_predecessor(["1" * 40, "2" * 40], "2" * 40)
        issuer.require_predecessor(["1" * 40], "0" * 40)
        with self.assertRaises(issuer.Refusal):
            issuer.require_predecessor(["1" * 40], "2" * 40)

    def test_cp4_rejects_binding_drift_before_object_reads(self):
        calls = []

        def forbidden_read(*args):
            calls.append(args)
            self.fail("invalid binding reached object reads")

        binding = {
            "repo": "soliskit/foundry-clean",
            "repo_id": 1466727123,
            "ref": "refs/heads/example",
            "head": "1" * 40,
            "old": "0" * 40,
            "app_id": 1,
            "installation_id": 1,
            "policy_sha256": "a" * 64,
            "source_sha256": "b" * 64,
        }
        for field, value in (
            ("ref", "refs/tags/example"),
            ("repo_id", True),
            ("head", "invalid"),
        ):
            with self.subTest(field=field):
                changed = dict(binding)
                changed[field] = value
                with self.assertRaises(publication_adapter.Stop):
                    publication_adapter.prepare(changed, forbidden_read, forbidden_read)
        self.assertEqual(calls, [])


def load_tests(loader, tests, pattern):
    import test_prospective_format

    tests.addTests(loader.loadTestsFromModule(test_prospective_format))
    return tests


if __name__ == "__main__":
    unittest.main()
