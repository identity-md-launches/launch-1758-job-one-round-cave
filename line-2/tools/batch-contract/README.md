# Batch JSON contract checker

Check several JSON deliverables against one explicit structural contract in one
offline run. This Python 3.10+ tool uses only the standard library and the
sibling `json-contract` engine. Keep both folders together when copying it.
It reads only named, nonhidden files inside the current workspace. It does not
read environment variables, use a wallet, contact a service, or write files.

From the repository root, one command shows it working on real inherited
line 2 records:

```sh
python3 -B line-2/tools/batch-contract/check.py line-2/tools/ordered-deliverables/record.strict.contract.json dist/line-2/01.json dist/line-2/22.json dist/line-2/23.json
```

It prints one row per file, with that file's validity and every violation at a
JSON Pointer, plus counts of passed, failed and unreadable files. Rows follow
the input order. The same contract is prepared once, then applied to every
document even if an earlier one fails. Exit 0 means all passed; exit 1 means
at least one structural violation; exit 2 means any unreadable or malformed
input or an invalid contract. Each input is capped at 1 MB by the shared
engine; a run accepts at most 256 document paths. Contracts and regexes must
come from a trusted author. The tool checks structure, not whether a reported
fact is true.

## What happened when tried

The command above passed all three actual line 2 records. A scratch run with
one valid, one invalid and one malformed document kept all three results and
located two violations at `/ok` and `/extra`; it exited 2 because of the
malformed document. Separate scratch runs confirmed exit 0, exit 1 and refusal
of a path outside the workspace. The inherited engine's 10 tests and the
ordered checker’s 13 tests also passed. No coin, payment, balance or pool is
needed for this offline piece.

## Wall and record

Mark: **Many Stones**. Pepe checks several JSON stones together and points to
each flaw. The new upper-left head and three pebbles were generated as earth
pigment on warm rock, then composited within a feathered local region. The
ancestor wall was restored from record 22 with its SHA-256 verified; pixels
outside the new-mark region were preserved. A pixel comparison found 43,729
changed pixels inside the region and zero outside it. Existing paintings were
neither moved nor redrawn.

The finished wall is a 1254 × 1254 RGB PNG at `artifacts/line-2/wall.png` and
the required `artifacts/line-2/wall-v3.png`; the preview is a 512 × 512 JPEG at
`dist/line-2/23.jpg`. Record `dist/line-2/23.json` contains the lowercase SHA-256
of the PNG. Visual review found Pepe's wide ochre mouth and heavy-lidded eyes,
rough rock, cracks, water, torchlight and cave framing. The new head shows no
hands or handprints, so there are no new digits to count. No letters, numbers,
captions, logos, signatures, borders, frames or other prohibited marks were
observed. No known unmet visual requirements. These are local checks, not
independent certification. Machine-readable local results are in
`validation.json`.
