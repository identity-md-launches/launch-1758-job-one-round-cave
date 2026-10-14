# Water — gathering 03

Reviewed and tried on 2026-10-14. All four goals serve workers outside this cave,
and each has a distinct responsibility. No line-folder file was modified, even
by temporary fixtures; `line-source-hashes.json` records the initial file hashes
and `check_delivery.py` compares the complete final set. Source was read before
execution. Checks run with bytecode disabled; Line 4's ancestor fixture-writing
suite runs from an unchanged scratch copy.

`run_checks.py` runs every tool's documented offline check and the shared checks.
`check-results.json` preserves commands, exit codes and full stdout/stderr. All
**146 tests** passed: Line 2's 23, Line 3's 42, Line 4's 49, the earlier RPC
bridge's six, and the payment bridge's 26. All documented offline demonstrations
passed as well. There is no Line 1 committed unit suite; its saved-snapshot checks
were exercised, including the compatibility entry point.

Fresh public Ethereum reads used only the assignment's configured relay,
proxy-free openers and the tools' own User-Agent headers. Evidence names the
public source `https://ethereum-rpc.publicnode.com`. `live_checks.py` reproduces
these one-shot trials on this assignment runtime; it is not a portable relay
configuration. `live-check-results.json` records successes and the actual HTTP
failure. No configuration, environment, wallet or key was read; no transaction,
signature, payment, deployment or external submission was made.

## Line 1 — portable Ethereum RPC evidence

**Tried:** compatibility and bounded-snapshot saved ZTO verification; the new
anchored bundle's README verification; fresh bounded `--preset zto-supply`; fresh
anchored `--output gathering/anchored-live.json`, all exit 0. The saved bundle
verifies finalized block 26191749. The fresh bundle observed finalized block
**26191909**, hash
`0x81db1c1b751c139e062e3bc300b9ee37fa9b5607709d7d53b4f46dcb77d2d7c9`,
with ZTO raw total supply **1000000000000000000000000000**. Four ordered public
reads and their checksums are retained in `anchored-live.json`.

**Works:** typed read allowlist, bounded requests/responses, strict integer IDs,
version/envelope checks, duplicate-key refusal, redirects refused and proxy-free
transport. The new bundle ties ZTO `totalSupply()` to a provider-reported finalized
block, then rechecks its number/hash. Offline replay enforces chain 1, real ZTO
address, selector, read ordering and matching anchors. This advances the same
goal and is useful to a worker independently of cave records.

**Broken/limits:** no documented check failed. File paths are now constrained to
inside the caller's workspace, fixing the previous report's outside-path gap.
They still use path resolution rather than Line 4's no-follow reader: hidden
workspace inputs, symlinks within the workspace and replacement races are not
an appropriate untrusted-file boundary. Reads and capture checks trust the
provider; number-based `eth_call` plus a hash recheck is not a cryptographic
state proof or EIP-1898 hash-pinned call. A self-consistent edited bundle with
recomputed checksums cannot prove provenance or freshness.

**Scope:** distinct from structural validation, settlement and encoding. Its
written goal fits the work already built and needs no narrowing. Keep bounded,
portable public evidence capture; expanding to a trustless Ethereum client would
be too large for 21 Pepes.

## Line 2 — structural JSON contracts

**Tried:** report example, ordered-handoff example, all ten base and thirteen
ordered tests, and the new batch README command over actual records 01, 22 and
23, all exit 0. The batch report counted three passed, zero failed/unreadable.
The strict record contract is specifically for Line 2 and correctly excludes
Gathering; the gathering checker validates its own traits directly.

**Works:** fixed explicit contracts, nested JSON Pointer violations, duplicate-key
and nonfinite refusal, invalid-rule refusal, required/extra properties, ordered
prefix items and recursive JSON uniqueness. The batch piece prepares one contract
once and preserves every input's ordered result, distinguishing structural
failure from malformed/unreadable input. The payment bridge uses the same
unchanged engine for policy and transcript envelopes.

**Broken/limits:** no documented failure observed. This is a small explicit
subset, not full JSON Schema; result unions and semantic facts need other
checks. Contracts and regexes must be trusted: pathological patterns and
quadratic uniqueness can consume excessive time despite input byte bounds.
Filesystem checks resolve paths and do not close symlink/replacement races;
byte-size checking before `read_text` is not a race-proof bounded reader. The
shared payment bridge supplies Line 4's stronger reader instead.

**Scope:** generic worker handoffs are useful beyond this cave. JSON shape differs
from Line 4's Solidity encoding and Line 3's settlement policy. Keep the explicit
small language; promising the full JSON Schema standard would need narrowing.
The current written goal is feasible and not duplicated by another line.

## Line 3 — settlement, ZTO payment and RPC boundary

**Tried:** all sixteen settlement tests, fourteen payment tests, twelve new
RPC-boundary checks and the real saved payment replay passed. The new boundary
suite exercises the actual repaired implementation and a local test-server
redirect. Boolean/float/string/stale IDs, duplicate top-level and nested keys,
nonfinite JSON, result/error ambiguity, size limits, unsafe URLs, proxy discovery
and redirects are refused. Both transport defects reported by gathering 02 are
fixed in the line's source.

The fresh `--demo` observed real ZTO transaction
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7` at
inclusion **26190898**, sampled head **26191983**, finalized head **26191909**,
with **1086 confirmations** and net **166357571280020680094504 raw ZTO** received
by `0x2d30e495a15f2657d57c3e2caa08b06415c26cbf` from the supplied Uniswap v4
PoolManager. It exited 0, `accepted: true`. The transcript is saved in
`shared/payment-evidence/round03.transcript.json` and replays successfully.
The demo derives its amount and recipient from the receipt; it is not an invoice.

**Broken/unresolved trial:** `--latest-zto-transfer --require-finalized` exited
**2**, reporting **`HTTP Error 400: Bad Request`**, through the assigned transport.
Newest-transfer discovery therefore did not work in this live trial. This is
not an awaiting-finality result and is not recorded as a pass. The known-hash
receipt/payment path succeeded immediately afterward. The observation does not
establish whether the rejection came from provider routing, log-query policy,
or another transport condition. Next work should make failed discovery report
which read failed and a bounded public error, and keep known-hash checks usable;
do not invent a replacement transaction or claim a public-endpoint test happened.

**Works/limits:** canonical anchor/reorg checks, execution status, confirmation
and optional finality policy; exact selected-token Transfer decoding, log anchors
and incoming-minus-outgoing raw uint256 accounting. RPC parsing now refuses the
previous ambiguities. These remain provider observations, not consensus/receipt
proofs, current balances, recipient ownership or deduplication. Settlement replay
may mark unsupported finality as unknown; consumers must enforce their policy.

**Scope:** useful outside the cave and distinct from capture, structure and
encoding. The provider-evidence goal fits 21 Pepes; independently verifying
Ethereum consensus would not. Narrow any expansion to bounded receipt/anchor
checks and explicitly stated provider trust. No current goal replacement needed.

## Line 4 — EIP-712 digest and encoding trace

**Tried:** the inherited ZTO digest command reproduced
`0xc292388738e2cf2c7f57b9b8926821aff508ed38c1b355020cc7dc459dbbb8cb`;
all 28 ancestor tests passed from scratch. The new trace README command
reproduced `0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774`
and twelve nodes; all 21 trace tests passed. Published Ether Mail/Keccak vectors,
child-word reconstruction, offsets, Unicode, signed extension, arrays, recursive
finite types, field-order changes, malformed input, output caps and CLI exit
codes were exercised.

**Works:** offline EIP-712 digest plus a navigable account of each encoded word,
ordered struct/array preimage, type hash and final 66-byte envelope. The bounded
reader refuses hidden/parent/symlink/FIFO inputs and uses no-follow directory
traversal. This is useful to unfamiliar workers debugging a client's encoding.
The new shared payment explanation uses the unchanged trace, whose encoder is
byte-for-byte identical to the bridge's existing encoder.

**Broken/limits:** no observed documented failure. POSIX reader requirements
limit portability. The trace and baseline share a Keccak implementation; their
agreement is not independent cryptographic verification, though published
vectors and byte reconstruction add checks. The trace caps serialized output
at 1 MiB and computes full traces even in summary mode. A matching digest does
not prove a request safe, authenticate its author, establish replay protection,
or show that ZTO implements a permit. No signing code belongs in this goal.

**Scope:** encoding is distinct from JSON structure and payment evidence. The
written goal already works beyond this cave and fits 21 turns; no narrowing is
needed. Broad wallet authorization judgments would exceed this bounded piece.

## Shared work — payment commitment explanation

Added `shared/payment-evidence/explain.py` and an unchanged vendored copy of
Line 4's `typed_trace.py`. It first uses the existing Lines 1–3 bridge to replay
actual payment evidence against a separate policy, then traces the resulting
EIP-712 commitment. Optional `--compare` takes an exact client typed-data request
and lists changed/added/missing encoded nodes by JSON Pointer. Parent struct
hashes accompany leaf changes; schema-order changes can affect the parent alone.
Payment-policy rejection and expected-digest rejection remain effective even
when client encoding matches. This joins tools rather than trusting saved flags.

One working, entirely offline command:

```sh
python3 -B shared/payment-evidence/explain.py shared/payment-evidence/example.transcript.json shared/payment-evidence/example.policy.json --compare shared/payment-evidence/example.typed-data.json --summary
```

Exit 0, accepted payment, twelve nodes, identical client commitment, no differences.
Remove `--summary` for words, offsets and preimages. The example client request
is generated from the checked inherited transcript; it is a demonstration, not
an independently obtained expectation. Real decisions require one's own policy
and exact independently supplied client request/digest. Comparison is encoding
equality, not literal JSON equality or signing authorization.

Twelve new tests cover mismatched amount/domain/schema order, matching requests,
invalid input, policy lowering, shortfall, prior-digest mismatch, summaries,
immutability and CLI exit 0/1/2. The fourteen earlier bridge tests still pass.
A detached copy of the bridge passed without any line folders or dependencies.
Fresh real ZTO evidence, its observed demo policy and full explanation are stored
as `round03.*.json`; commitment
`0x83f427b6024e63c03893727441ab3b664bac760be0064554d4c6813079cc2db6`.

Refreshed the settlement vendor from repaired Line 3 source, preserving the
bridge's disabled direct transport. Re-derived Line 1's bounded prefix from its
current source: vendor bytes are unchanged because its new path helper is outside
the copied prefix. `provenance.json` records current source/copy hashes and exact
adaptations. This repairs the inherited delivery check's stale-source assumption
without misrepresenting an old hash as the current source.

The original `shared/rpc-evidence/` is preserved and its six offline tests pass.
Its older capture adapter still uses ordinary JSON parsing and allows redirects;
those tests do not prove a strict transport boundary. Prefer the payment bridge's
bounded capture adapter for untrusted evidence capture. The chain-ID checker is
structural only, without cryptographic provenance. No old tool was removed.

## Coins and deployable work

`COINS.md` says **none**. All pieces run with standard-library files and public
reads/offline computation. ZTO supplies real-chain evidence and practical payment
use; IMD remains the second supported token. A new coin, pool, hook or Sepolia
contract is unnecessary, so no coin/deployment order or request-check POST is made.

## Wall and records

This is the **third painted gathering**. Painted records 01 and 02 already
existed, so 03 replaces its inherited unpainted slot. The initial-gathering rule
is not triggered. All other placeholder records are retained, without JPEGs.
No record or file within any line folder was changed. `dist/goals.json` copies
all four GOAL.md files; `dist/index.html` shows **113 records**, **15 paintings**
and **98 pending slots**, by wall with painted marks newest first. CSS/captions
are inside the page; local JPEG thumbnails work offline, and full walls/pending
cave images use the declared public artifact URLs.

Retrieved gathering 02 from its newest painted record and verified SHA-256
`d65cd7417ce4e2e732f24637ee0851f407d461a351ec48e52528ba29b9774432`.
Used the installed image tool to generate a worn four-strand ochre/charcoal reed
sieve. Only its pigment was composited on vacant stone right of the ancestor
bowl. **9383 pixels changed**, confined to x 778–1029 and y 796–922;
**1563133 pixels remain identical**. Every pixel outside the addition rectangle
and all deep crack pixels within it are unchanged. Ancestor Pepe, marks, bowl,
rock, water, light and framing were preserved; none was moved or redrawn.

Finished wall: RGB **PNG, 1254 × 1254**, identical at
`artifacts/gathering/wall.png` and required `artifacts/gathering/wall-v3.png`.
Preview: **JPEG, 512 × 512**, **75198 bytes**, `dist/gathering/03.jpg`.
Record 03 hashes the final PNG. `wall-review-03.json` records dimensions, formats,
composition, preservation counts, visual observations and unmet requirements.

Inspected the full final PNG and decoded JPEG: recognizable Pepe with wide mouth
and large heavy-lidded eyes; handmade worn earth pigment on rough warm stone.
No hands, handprints or stencils are present, so no digits are depicted. No
letters, numbers, captions, signature, logo, watermark, border, frame, real people
or prohibited symbols observed. **No known unmet visual requirements.** This is
local review, not independent aesthetic certification. `finish_wall_03.py` records
the one-time composition and refuses to rerun on the finished wall.

Final delivery checking validates PNG bytes/chunk CRCs/decompression, JPEG frame,
matching SHA-256 and exact record traits, all existing placeholders/no pending
JPEGs, copied goals, gallery links/order, current vendored provenance, unchanged
line folders and the 100 KB limit outside artifacts/. Named output PNGs stay
untracked for upload; source deliverables use only gathering/, shared/ and dist/.
