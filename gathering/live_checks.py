#!/usr/bin/env python3
"""One-shot public-read trials using the assignment's Ethereum relay."""
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import io
import json
from pathlib import Path
import sys
import urllib.request
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = 'https://ethereum-rpc.publicnode.com'
# Assignment transport only; all evidence continues to name the public source.
RELAY = 'http://127.0.0.1:43283/rpc/1'


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def main():
    if Path.cwd().resolve() != ROOT:
        raise SystemExit('Run from the repository root')
    snapshot = module('live_snapshot', 'line-1/tools/bounded-rpc-snapshot/snapshot.py')
    anchored = module('live_anchored', 'line-1/tools/anchored-zto-snapshot/anchored.py')
    witness = module('live_witness', 'line-3/tools/payment-witness/witness.py')
    settlement = witness.settlement
    original = urllib.request.Request

    def request(url, *args, **kwargs):
        if url == PUBLIC:
            url = RELAY
        else:
            raise ValueError('trial only allows the assigned public Ethereum source')
        return original(url, *args, **kwargs)

    results = []
    with patch.object(urllib.request, 'Request', request):
        for label, function, args in [
                ('line1 bounded ZTO supply', snapshot.main, ['--preset', 'zto-supply']),
                ('line1 finalized ZTO bundle', anchored.main,
                 ['--output', 'gathering/anchored-live.json']),
                ('line3 newest ZTO settlement', settlement.main,
                 ['--latest-zto-transfer', '--require-finalized']),
                ('line3 real ZTO payment', witness.main, ['--demo'])]:
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = function(args)
            text = out.getvalue()
            row = {'trial': label, 'source': PUBLIC, 'exitCode': code,
                   'stdout': text, 'stderr': err.getvalue()}
            if label.startswith('line3') and code == 0:
                report = json.loads(text)
                sample = report.pop('sample')
                bridge = ROOT / 'shared/payment-evidence'
                (bridge / 'round03.transcript.json').write_text(json.dumps(sample, indent=2)+'\n')
                (bridge / 'round03.policy.json').write_text(json.dumps(sample['policy'], indent=2)+'\n')
                row['stdout'] = json.dumps(report, indent=2)
            results.append(row)
            print(label, 'exit', code, flush=True)
    (ROOT / 'gathering/live-check-results.json').write_text(json.dumps(results, indent=2)+'\n')
    # A well-formed strict settlement rejection is a useful observed result.
    return 0 if all(row['exitCode'] == 0 or
                    (row['trial'] == 'line3 newest ZTO settlement' and row['exitCode'] == 1)
                    for row in results) else 1


if __name__ == '__main__':
    sys.exit(main())
