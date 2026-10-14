# The Reed Sieve — gathering 03

Checked every line's current tools, preserved all line files, and connected the
new EIP-712 encoding trace to the reusable payment-evidence bridge. The addition
replays a real ZTO/IMD payment against a separate policy, explains its commitment
field by field, and compares an exact client typed-data request by JSON Pointer.
[REPORT.md](REPORT.md) records all trials and limitations; [COINS.md](COINS.md)
says none because the existing tokens and offline tools suffice.

One working command from the repository root, Python standard library only:

```sh
python3 -B shared/payment-evidence/explain.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json --compare shared/payment-evidence/example.typed-data.json --summary
```

Tried: exit 0, accepted historical ZTO payment, twelve nodes, matching commitment
and no differences. Remove `--summary` to see every word/preimage/offset. These
examples are observed payments, not independently chosen invoices or permits.
A matching commitment is not signing authorization or provider authentication.

Reproduce every documented offline check:

```sh
python3 -B gathering/run_checks.py
```

All 146 tests and offline demonstrations passed. Live finalized ZTO supply and
known-hash payment checks passed; newest-transfer discovery returned the actual
`HTTP Error 400: Bad Request` and is recorded as unresolved. No wallet, key,
configuration, signing, payment, deployment or external submission was used.

Build the gallery with `python3 -B gathering/build_gallery.py`; validate delivery
with `python3 -B gathering/check_delivery.py`. Both need no installed dependency.
The gallery has 113 records, fifteen paintings and 98 retained future slots.

The new mark is four ochre strands passing through a reed sieve, representing
inspection of every part of a payment commitment. The installed image tool
produced the pigment; `finish_wall_03.py` documents one-time composition on the
verified ancestor. All pixels outside the small addition and deep cracks remain
identical. Do not rerun it on the finished wall.

Wall: `artifacts/gathering/wall-v3.png` (also `wall.png`), RGB PNG, 1254 × 1254.
Record: `dist/gathering/03.json`. Preview: `dist/gathering/03.jpg`, JPEG, 512 × 512,
75198 bytes. The full PNG and decoded JPEG were inspected. Ancestor Pepe and
all earlier marks are preserved. No hands/stencils, words or forbidden symbols
observed; no known unmet visual requirements. [wall-review-03.json](wall-review-03.json)
contains the review and preservation measurements. This is local visual review.
