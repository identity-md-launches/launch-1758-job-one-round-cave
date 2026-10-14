# Offline EIP-712 encoding trace

This standalone Python standard-library tool explains the bytes behind an EIP-712
digest. Each field has a JSON Pointer and a 32-byte encoded word. Structs show the
ordered fields, byte offsets, canonical type encoding, type hash and full hash
input. Arrays show each element's word and offset; strings and dynamic bytes show
their exact UTF-8 or binary hash input. The report ends with the 66-byte EIP-712
envelope. This helps an unfamiliar worker locate an encoding disagreement before
trusting a client's displayed digest.

Run from the workspace root:

```sh
python3 -B line-4/tools/typed-trace/typed_trace.py line-4/tools/typed-trace/zto-payment.json --expect 0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774
```

It exits **0**, emits twelve trace nodes, and reports `matchesExpected: true`.
Add `--summary` to print only the hashes and node count. Remove `--expect` to
calculate without comparison. A valid digest mismatch exits **1**; malformed
input or an invalid expected digest exits **2**, with an error on stderr and no
success report on stdout. Neither mode signs or sends anything. The whole folder
can be copied into a different workspace and run without other line folders,
packages, configuration, accounts, environment access or network access.

The example commits to a real historical ZTO payment observation, extracted
unchanged from the inherited payment-evidence report. Its transaction is
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7`.
On 2026-10-14 a fresh public receipt read confirmed the ZTO Transfer at log 632:
`166357571280020680094504` raw units received by
`0x2d30e495a15f2657d57c3e2caa08b06415c26cbf` from the supplied Uniswap v4
PoolManager at block 26190898. The read is saved in `example-source.json`; the
public source is [Ethereum PublicNode](https://ethereum-rpc.publicnode.com).
The example's `transcriptHash` commits to the inherited report's historical
transcript, rather than the fresh receipt file. Its twelve-confirmation policy
is the inherited demonstration policy. It is a content commitment, not a token
permit, independently chosen invoice, signature, proof of current finality, or
claim that ZTO accepts the message. `provenance.json` identifies the original
report and unchanged copied encoder by SHA-256.

To use another request, supply its exact `types`, `primaryType`, `domain` and
`message`, including the explicit `EIP712Domain` declaration, and independently
obtain the expected digest. Nodes are listed children before parents, so each
parent's field words can be looked up by path. All offsets are zero-based byte
offsets **within that node's preimage**. A struct's first 32 bytes are its type
hash. Atomic nodes have no hash preimage because their word is directly padded
or sign-extended; integer `normalizedValue` is a decimal string to retain all
256 bits in clients that round JSON numbers. Hashing uses Ethereum Keccak-256,
as specified by [EIP-712](https://eips.ethereum.org/EIPS/eip-712).

Tried on 2026-10-14:

- All **21 new tests** passed, including the published Ether Mail digest,
  reconstructing every preimage from child words, byte offsets, Unicode UTF-8,
  signed extension, fixed-byte padding, nested arrays, finite recursive structs,
  schema-order sensitivity, input refusal, trace size bounds and CLI exit codes.
- All **28 ancestor tests** passed from an unchanged copy in scratch.
- A detached copy of this folder reproduced the ZTO digest without the ancestor
  folder or shared payment tool. The original example and goal remain unchanged.
- The fresh receipt's real token, recipient and raw Transfer amount matched the
  inherited example. The tool's normal demonstration remains entirely offline.

Run the new suite:

```sh
python3 -B -m unittest discover -s line-4/tools/typed-trace -p 'test_*.py' -v
```

The CLI reuses the ancestor's bounded JSON reader: regular files beneath the
current working directory only, no hidden components, parent traversal or
symlinks; POSIX no-follow directory descriptors are required. Input is limited
to 65,536 bytes, depth 48, 8,192 visited values/keys, 64 struct declarations,
256 total fields and eight array dimensions. Duplicate keys, floats,
nonfinite numbers, invalid Unicode, cycles and invalid values are refused.
The complete trace is additionally capped at **1,048,576 serialized bytes**;
oversize traces fail rather than omit fields. Summary mode still computes and
checks the complete trace. Output goes to stdout; the tool does not write files.
Only the tests create disposable fixtures beneath `test/scratch/`.

The trace cross-checks the ancestor's digest, but both use the same Keccak
primitive; this is not an independent second cryptographic implementation. The
published vector and explicit byte reconstruction are additional checks. A
matching digest does not establish signing safety, requester identity, replay
protection, contract support or truth of a claimed payment. Bounds limit work;
they do not establish an operating-system or wall-clock sandbox.
