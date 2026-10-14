"""Published-vector, byte reconstruction, semantic and boundary regressions."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import typed_trace
from typed_digest import TypedDataError, keccak256, load_workspace_json
from typed_trace import explain

HERE = Path(__file__).resolve().parent
EXAMPLE = HERE / "zto-payment.json"
EXPECTED = "0xf33e2506e5c103f98dbfe3feb6d4b87d55f1fad4e423dbaa8462465ff4ab9774"


def request(kind, value):
    return {"types": {"EIP712Domain": [], "Data": [{"name": "value", "type": kind}]},
            "primaryType": "Data", "domain": {}, "message": {"value": value}}


def nodes(report):
    return {node["path"]: node for node in report["nodes"]}


def raw(value):
    return bytes.fromhex(value[2:])


class TraceTests(unittest.TestCase):
    def test_real_zto_historical_commitment(self):
        result = explain(load_workspace_json(EXAMPLE), EXPECTED)
        self.assertTrue(result["matchesExpected"])
        self.assertEqual(result["digest"], EXPECTED)
        self.assertEqual(len(result["nodes"]), 12)
        token = nodes(result)["/message/token"]
        self.assertEqual(token["word"], "0x" + "00" * 12 +
                         "d782bdea4ef02a0bd391eb9089470c8080f0a68e")
        amount = nodes(result)["/message/minimumRaw"]
        self.assertEqual(int.from_bytes(raw(amount["word"]), "big"),
                         166357571280020680094504)

    def test_published_ether_mail_vector(self):
        data = {
            "types": {
                "EIP712Domain": [{"name": n, "type": t} for n, t in
                                 [("name", "string"), ("version", "string"),
                                  ("chainId", "uint256"), ("verifyingContract", "address")]],
                "Person": [{"name": "name", "type": "string"},
                           {"name": "wallet", "type": "address"}],
                "Mail": [{"name": "from", "type": "Person"},
                         {"name": "to", "type": "Person"},
                         {"name": "contents", "type": "string"}]},
            "primaryType": "Mail",
            "domain": {"name": "Ether Mail", "version": "1", "chainId": 1,
                       "verifyingContract": "0xCcCCccccCCCCcCCCCCCcCcCccCcCCCcCcccccccC"},
            "message": {
                "from": {"name": "Cow", "wallet": "0xCD2a3d9F938E13CD947Ec05AbC7FE734Df8DD826"},
                "to": {"name": "Bob", "wallet": "0xbBbBBBBbbBBBbbbBbbBbbbbBBbBbbbbBbBbbBBbB"},
                "contents": "Hello, Bob!"}}
        result = explain(data)
        self.assertEqual(result["domainSeparator"],
                         "0xf2cee375fa42b42143804025fc449deafd50cc031ca257e0b194a650a912090f")
        self.assertEqual(result["messageHash"],
                         "0xc52c0ee5d84264471806290a3f2c4cecfc5490626bf912d01f240d7a274b371e")
        self.assertEqual(result["digest"],
                         "0xbe609aee343fb3c4b28e1df9e632fca64fcfaede20f02e86244efddf30957bd2")
        self.assertEqual(nodes(result)["/message/from"]["typeEncoding"],
                         "Person(string name,address wallet)")

    def test_every_hash_can_be_rebuilt_from_trace(self):
        result = explain(request("string[]", ["hello", "", "\U0001f438"]))
        known = {}
        for node in result["nodes"]:
            if "preimage" in node:
                preimage = raw(node["preimage"])
                self.assertEqual(len(preimage), node["preimageBytes"])
                self.assertEqual(keccak256(preimage), raw(node["word"]))
            if node["kind"] == "struct":
                self.assertEqual(keccak256(node["typeEncoding"].encode()), raw(node["typeHash"]))
                words = [raw(node["typeHash"])]
                for i, field in enumerate(node["fields"], 1):
                    self.assertEqual(field["offsetBytes"], 32 * i)
                    self.assertEqual(field["word"], known[field["path"]])
                    words.append(raw(field["word"]))
                self.assertEqual(b"".join(words), raw(node["preimage"]))
            if node["kind"] == "array":
                words = []
                for i, element in enumerate(node["elements"]):
                    self.assertEqual(element["offsetBytes"], 32 * i)
                    self.assertEqual(element["word"], known[element["path"]])
                    words.append(raw(element["word"]))
                self.assertEqual(b"".join(words), raw(node["preimage"]))
            self.assertNotIn(node["path"], known)
            known[node["path"]] = node["word"]
        envelope = result["envelope"]
        preimage = b"\x19\x01" + raw(known["/domain"]) + raw(known["/message"])
        self.assertEqual(preimage, raw(envelope["preimage"]))
        self.assertEqual(len(preimage), 66)
        self.assertEqual(keccak256(preimage), raw(result["digest"]))

    def test_signed_extension_and_integer_string_normalization(self):
        for value in (-1, "-1"):
            leaf = nodes(explain(request("int8", value)))["/message/value"]
            self.assertEqual(leaf["word"], "0x" + "ff" * 32)
            self.assertEqual(leaf["normalizedValue"], "-1")
        for value in (255, "255", "0xff"):
            leaf = nodes(explain(request("uint8", value)))["/message/value"]
            self.assertEqual(leaf["word"], "0x" + "00" * 31 + "ff")
            self.assertEqual(leaf["normalizedValue"], "255")

    def test_fixed_bytes_right_padding_and_dynamic_bytes_hashing(self):
        fixed = nodes(explain(request("bytes2", "0x12AB")))["/message/value"]
        self.assertEqual(fixed["word"], "0x12ab" + "00" * 30)
        dynamic = nodes(explain(request("bytes", "0x12AB")))["/message/value"]
        self.assertEqual(dynamic["preimage"], "0x12ab")
        self.assertEqual(raw(dynamic["word"]), keccak256(b"\x12\xab"))

    def test_unicode_utf8_preimage(self):
        text = "caf\u00e9 \U0001f438"
        leaf = nodes(explain(request("string", text)))["/message/value"]
        self.assertEqual(raw(leaf["preimage"]), text.encode("utf-8"))
        self.assertEqual(leaf["inputBytes"], 10)

    def test_empty_array_and_empty_string(self):
        for kind, value in (("uint8[]", []), ("string", ""), ("bytes", "0x")):
            with self.subTest(kind=kind):
                leaf = nodes(explain(request(kind, value)))["/message/value"]
                self.assertEqual(leaf["preimage"], "0x")
                self.assertEqual(leaf["word"],
                                 "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")

    def test_nested_fixed_array_order(self):
        report = explain(request("uint8[2][2]", [[1, 2], [3, 4]]))
        leaves = nodes(report)
        self.assertEqual(raw(leaves["/message/value/0"]["preimage"]),
                         (1).to_bytes(32, "big") + (2).to_bytes(32, "big"))
        self.assertEqual(raw(leaves["/message/value/1"]["preimage"]),
                         (3).to_bytes(32, "big") + (4).to_bytes(32, "big"))
        self.assertEqual(raw(leaves["/message/value"]["preimage"]),
                         raw(leaves["/message/value/0"]["word"]) +
                         raw(leaves["/message/value/1"]["word"]))

    def test_recursive_struct_array_with_finite_value(self):
        data = {"types": {"EIP712Domain": [], "Node": [
                    {"name": "children", "type": "Node[]"}]},
                "primaryType": "Node", "domain": {},
                "message": {"children": [{"children": []}]}}
        report = explain(data)
        leaves = nodes(report)
        self.assertEqual(leaves["/message/children/0/children"]["preimage"], "0x")
        self.assertEqual(leaves["/message"]["typeEncoding"], "Node(Node[] children)")
        self.assertEqual(len(report["nodes"]), 5)

    def test_message_object_key_order_does_not_change_trace(self):
        data = load_workspace_json(EXAMPLE)
        changed = copy.deepcopy(data)
        changed["message"] = dict(reversed(list(changed["message"].items())))
        self.assertEqual(explain(data), explain(changed))

    def test_declared_field_order_does_change_trace(self):
        data = load_workspace_json(EXAMPLE)
        changed = copy.deepcopy(data)
        changed["types"]["PaymentEvidence"].reverse()
        left, right = explain(data), explain(changed)
        self.assertNotEqual(left["digest"], right["digest"])
        self.assertNotEqual(nodes(left)["/message"]["preimage"], nodes(right)["/message"]["preimage"])

    def test_request_not_mutated(self):
        data = load_workspace_json(EXAMPLE)
        before = copy.deepcopy(data)
        explain(data)
        self.assertEqual(data, before)

    def test_rejected_value_has_no_trace(self):
        for kind, value in (("uint8", 256), ("bool", 1), ("uint8[2]", [1]),
                            ("string", "\ud800"), ("bytes", "0x1")):
            with self.subTest(kind=kind), self.assertRaises(TypedDataError):
                explain(request(kind, value))

    def test_bad_schema_and_cycles_rejected(self):
        data = request("uint8", 1)
        data["message"]["extra"] = True
        with self.assertRaises(TypedDataError):
            explain(data)
        data = request("uint8[]", [])
        data["message"]["value"].append(data["message"]["value"])
        with self.assertRaises(TypedDataError):
            explain(data)

    def test_invalid_expected_digest(self):
        with self.assertRaises(TypedDataError):
            explain(load_workspace_json(EXAMPLE), "0x1234")

    def test_output_budget_rejects_instead_of_truncating(self):
        with patch.object(typed_trace, "MAX_TRACE_BYTES", 500):
            with self.assertRaisesRegex(TypedDataError, "output limit"):
                explain(load_workspace_json(EXAMPLE))

    def test_detects_internal_trace_disagreement(self):
        with patch.object(typed_trace.Trace, "value", return_value=keccak256(b"incorrect")):
            with self.assertRaisesRegex(TypedDataError, "disagrees"):
                explain(load_workspace_json(EXAMPLE))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(HERE / "typed_trace.py"),
                               *map(str, args)], capture_output=True, text=True, timeout=10)

    def test_full_and_summary_match(self):
        for options in ([], ["--summary"]):
            result = self.run_cli(EXAMPLE, "--expect", EXPECTED, *options)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["matchesExpected"])
            self.assertEqual(report["digest"], EXPECTED)
            if options:
                self.assertEqual(report["traceNodes"], 12)
                self.assertNotIn("nodes", report)

    def test_full_and_summary_mismatch_exit_one(self):
        different = "0x" + keccak256(b"different digest").hex()
        for options in ([], ["--summary"]):
            result = self.run_cli(EXAMPLE, "--expect", different, *options)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(json.loads(result.stdout)["matchesExpected"])

    def test_bad_expected_and_unsafe_paths_exit_two(self):
        for args in ((EXAMPLE, "--expect", "0x1234"), ("../outside.json",),
                     (".hidden.json",)):
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_json_and_oversize_file_exit_two(self):
        scratch = Path.cwd() / "test/scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="typed-trace-", dir=scratch) as folder:
            path = Path(folder) / "request.json"
            for raw_input in (b'{"types":{},"types":{}}', b" " * 65537):
                path.write_bytes(raw_input)
                result = self.run_cli(path)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
