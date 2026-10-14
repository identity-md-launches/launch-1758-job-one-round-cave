# RPC boundary checks

A portable, Python standard-library regression probe for the public-read transport
used by line 3's settlement and ZTO payment tools. It accompanies the repaired
`settlement-check/settlement.py`; keep that sibling folder when copying this piece.
No install or network is needed. It tests the actual imported RPC implementation,
not a separate parser. One test briefly runs a loopback HTTP server to prove that
a redirect is rejected without requesting its target. It never sends to Ethereum,
reads environment variables, signs, pays, or uses a wallet.

One command from the repository root shows the repaired boundary working:

```sh
python3 -B line-3/tools/rpc-boundary/check.py
```

What happened when tried: all **12 checks passed**. They exercise boolean, float,
string and stale IDs; duplicate top-level, nested and escaped-equivalent keys;
nonfinite constants; invalid UTF-8, malformed JSON and excessive nesting; exclusive
result/error envelopes; null results; the 4 MB response cap; URL validation;
request ID/header preservation; the read-method allowlist; refusal of proxy
configuration discovery; and a real local HTTP redirect. The prior 16 settlement
and 14 payment tests also passed. Exit 0 means every check passed; a nonzero exit
means a regression or inability to run the loopback test.

The existing settlement transport now requires an exact integer response ID,
refuses duplicate keys at every nesting depth and nonfinite constants, requires
exactly one result/error field, disables environment-derived proxies, and refuses
redirects. HTTP(S) URLs require a host and cannot embed credentials, whitespace or
a fragment. These changes apply automatically to payment-witness, which imports
that module. Its confirmation, canonical-anchor and finality policies are unchanged.

A real-chain check through the repaired transport also passed:

```sh
python3 -B line-3/tools/payment-witness/witness.py --demo
```

`live-check.json` records that run against publicnode: real ZTO transaction
`0xc4ca304c305cae326cab066639ab2156412eee7f5f774b41a2a136369f817ef7`,
inclusion 26190898, sampled head 26191877, 980 confirmations, finalized head
26191813, net `166357571280020680094504` raw ZTO to recipient
`0x2d30e495a15f2657d57c3e2caa08b06415c26cbf`. It returned `accepted: true`.
The demo derives its threshold from the observed receipt, so it demonstrates
transport and decoding rather than verifying an independently issued invoice.
The file records historical observations, not current chain status.

This is transport ambiguity protection, not authentication of a provider's claims.
A dishonest provider can still supply a consistently false receipt or chain.
Response bytes and timeout are bounded, but this is not an OS sandbox or a
consensus verifier. Proxy-only networks must provide direct access or use a
separately reviewed transport; automatic proxy discovery is deliberately disabled.
