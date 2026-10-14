"""Payment replay plus encoding comparison, using real saved evidence offline."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check import HERE, check, load
from explain import explain_payment


class ExplainTests(unittest.TestCase):
    def setUp(self):
        self.sample = load(HERE / 'example.transcript.json')
        self.policy = load(HERE / 'example.policy.json')
        self.data = check(self.sample, self.policy)['typedData']

    def test_payment_trace_preserves_commitment(self):
        result = explain_payment(self.sample, self.policy)
        self.assertTrue(result['accepted'])
        self.assertFalse(result['providerAuthenticated'])
        self.assertEqual(result['encodingTrace']['digest'],
                         check(self.sample, self.policy)['commitment']['digest'])
        self.assertEqual(result['encodingTrace']['envelope']['preimageBytes'], 66)
        self.assertEqual(len(result['encodingTrace']['nodes']), 12)

    def test_exact_client_request_matches(self):
        result = explain_payment(self.sample, self.policy, self.data)
        self.assertTrue(result['accepted'])
        self.assertTrue(result['comparison']['matchesCommitment'])
        self.assertEqual(result['comparison']['differences'], [])

    def test_changed_amount_locates_leaf_and_parent(self):
        self.data['message']['minimumRaw'] = str(int(self.policy['minimum_raw']) + 1)
        result = explain_payment(self.sample, self.policy, self.data)
        self.assertTrue(result['paymentAccepted'])
        self.assertFalse(result['accepted'])
        rows = {r['path']: r for r in result['comparison']['differences']}
        self.assertEqual(set(rows), {'/message', '/message/minimumRaw'})
        self.assertEqual(int(rows['/message/minimumRaw']['expectedWord'], 16),
                         int(self.policy['minimum_raw']))

    def test_changed_domain_locates_leaf(self):
        self.data['domain']['chainId'] = 8453
        result = explain_payment(self.sample, self.policy, self.data)
        self.assertFalse(result['accepted'])
        self.assertEqual({r['path'] for r in result['comparison']['differences']},
                         {'/domain', '/domain/chainId'})

    def test_changed_field_order_changes_struct_word(self):
        self.data['types']['PaymentEvidence'].reverse()
        result = explain_payment(self.sample, self.policy, self.data)
        self.assertFalse(result['accepted'])
        self.assertEqual([r['path'] for r in result['comparison']['differences']], ['/message'])

    def test_missing_client_field_is_invalid(self):
        del self.data['message']['recipient']
        with self.assertRaises(ValueError):
            explain_payment(self.sample, self.policy, self.data)

    def test_lowered_transcript_policy_cannot_be_explained_as_valid(self):
        self.sample['policy']['minimum_raw'] = '1'
        with self.assertRaisesRegex(ValueError, '/policy'):
            explain_payment(self.sample, self.policy)

    def test_shortfall_stays_rejected_despite_matching_request(self):
        self.policy['minimum_raw'] = str(int(self.policy['minimum_raw']) + 1)
        self.sample['policy'] = copy.deepcopy(self.policy)
        data = check(self.sample, self.policy)['typedData']
        result = explain_payment(self.sample, self.policy, data)
        self.assertTrue(result['comparison']['matchesCommitment'])
        self.assertFalse(result['paymentAccepted'])
        self.assertFalse(result['accepted'])

    def test_expected_digest_mismatch_stays_rejected(self):
        other = check(self.sample, self.policy)['commitment']['domainSeparator']
        result = explain_payment(self.sample, self.policy, self.data, other)
        self.assertTrue(result['comparison']['matchesCommitment'])
        self.assertFalse(result['matchesExpectedDigest'])
        self.assertFalse(result['accepted'])

    def test_summary_same_decision_and_digest(self):
        full = explain_payment(self.sample, self.policy, self.data)
        summary = explain_payment(self.sample, self.policy, self.data, summary=True)
        self.assertEqual(full['accepted'], summary['accepted'])
        self.assertEqual(full['commitment'], summary['commitment'])
        self.assertNotIn('encodingTrace', summary)
        self.assertEqual(summary['traceNodes'], 12)

    def test_inputs_unchanged(self):
        before = copy.deepcopy((self.sample, self.policy, self.data))
        explain_payment(self.sample, self.policy, self.data)
        self.assertEqual((self.sample, self.policy, self.data), before)

    def test_cli_three_exit_codes(self):
        command = [sys.executable, '-B', str(HERE / 'explain.py'),
                   str(HERE / 'example.transcript.json'), str(HERE / 'example.policy.json')]
        result = subprocess.run(command + ['--summary'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        scratch = Path.cwd() / 'test/scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as folder:
            path = Path(folder) / 'client.json'
            self.data['domain']['chainId'] = 8453
            path.write_text(json.dumps(self.data))
            result = subprocess.run(command + ['--compare', str(path)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(json.loads(result.stdout)['accepted'])
            path.write_text('{"x":1,"x":2}')
            result = subprocess.run(command + ['--compare', str(path)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertFalse(json.loads(result.stdout)['accepted'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
