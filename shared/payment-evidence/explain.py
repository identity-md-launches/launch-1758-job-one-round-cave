#!/usr/bin/env python3
"""Replay payment evidence, trace its commitment and compare a supplied request."""
import argparse
import json
import sys

from check import HERE, check, load

# The two copied Line 4 modules are kept together for portable offline use.
sys.path.insert(0, str(HERE / 'vendor'))
from typed_trace import explain as trace


def differences(expected, supplied):
    """Compare encoded words by JSON Pointer, including parent hash changes."""
    left = {n['path']: n for n in expected['nodes']}
    right = {n['path']: n for n in supplied['nodes']}
    rows = []
    for path in sorted(left.keys() | right.keys()):
        a, b = left.get(path), right.get(path)
        if a is None or b is None or (a['type'], a['word']) != (b['type'], b['word']):
            rows.append({'path': path,
                         'expectedType': a['type'] if a else None,
                         'suppliedType': b['type'] if b else None,
                         'expectedWord': a['word'] if a else None,
                         'suppliedWord': b['word'] if b else None})
    return rows


def explain_payment(sample, policy, supplied=None, expect_digest=None, summary=False):
    evidence = check(sample, policy, expect_digest)
    encoding = trace(evidence['typedData'], evidence['commitment']['digest'])
    comparison = None
    if supplied is not None:
        other = trace(supplied)
        comparison = {
            'matchesCommitment': other['digest'] == encoding['digest'],
            'suppliedDigest': other['digest'],
            'differences': differences(encoding, other)}
    accepted = evidence['accepted'] and (comparison is None or comparison['matchesCommitment'])
    result = {'accepted': accepted,
              'paymentAccepted': evidence['settlementAndPayment']['accepted'],
              'matchesExpectedDigest': evidence['matchesExpectedDigest'],
              'providerAuthenticated': False,
              'evidenceMode': evidence['evidenceMode'],
              'settlementAndPayment': evidence['settlementAndPayment'],
              'commitment': evidence['commitment'],
              'comparison': comparison}
    if summary:
        result['traceNodes'] = len(encoding['nodes'])
    else:
        result['typedData'] = evidence['typedData']
        result['encodingTrace'] = encoding
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transcript')
    parser.add_argument('policy', help='independently supplied payment policy')
    parser.add_argument('--compare', help='exact client typed-data JSON to compare')
    parser.add_argument('--expect-digest', help='independently obtained prior commitment')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = explain_payment(load(args.transcript), load(args.policy),
                                 load(args.compare) if args.compare else None,
                                 args.expect_digest, args.summary)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0 if result['accepted'] else 1
    except (ValueError, OSError, TypeError, KeyError, RecursionError) as exc:
        print(json.dumps({'accepted': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
