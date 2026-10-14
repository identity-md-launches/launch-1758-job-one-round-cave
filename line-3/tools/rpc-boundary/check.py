#!/usr/bin/env python3
"""Offline regression checks for settlement's public-read RPC boundary."""
import importlib.util
import io
import json
from pathlib import Path
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    'settlement', Path(__file__).resolve().parent.parent / 'settlement-check' / 'settlement.py')
s = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s)


class MemoryOpener:
    def __init__(self, body):
        self.body = body
        self.requests = []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        return io.BytesIO(self.body)


class BoundaryTests(unittest.TestCase):
    def call(self, body):
        rpc = s.RPC(s.RPC_URL)
        rpc.opener = MemoryOpener(body)
        return rpc.call('eth_chainId', [])

    def test_integer_id_and_null_result(self):
        self.assertEqual(self.call(b'{"jsonrpc":"2.0","id":1,"result":"0x1"}'), '0x1')
        self.assertIsNone(self.call(b'{"jsonrpc":"2.0","id":1,"result":null}'))

    def test_exact_id_type(self):
        for value in ('true', 'false', '1.0', '"1"', 'null', '2', '[]', '{}'):
            with self.subTest(value=value), self.assertRaises(s.EvidenceError):
                self.call(('{"jsonrpc":"2.0","id":'+value+',"result":"0x1"}').encode())

    def test_duplicate_keys_including_nested(self):
        for body in (
            b'{"jsonrpc":"2.0","id":1,"result":"0x2","result":"0x1"}',
            b'{"jsonrpc":"2.0","id":2,"id":1,"result":"0x1"}',
            b'{"jsonrpc":"2.0","id":1,"result":{"logs":[{"removed":true,"removed":false}]}}',
            b'{"jsonrpc":"2.0","id":1,"result":{"a":1,"\\u0061":2}}',
        ):
            with self.subTest(body=body), self.assertRaises(s.EvidenceError):
                self.call(body)

    def test_nonfinite_anywhere(self):
        for value in ('NaN', 'Infinity', '-Infinity'):
            with self.subTest(value=value), self.assertRaises(s.EvidenceError):
                self.call(('{"jsonrpc":"2.0","id":1,"result":['+value+']}').encode())

    def test_envelope_exclusive_result_error(self):
        for fields in ('', ',"error":{"code":-1}', ',"result":null,"error":null'):
            with self.subTest(fields=fields), self.assertRaises(s.EvidenceError):
                self.call(('{"jsonrpc":"2.0","id":1'+fields+'}').encode())

    def test_bad_encoding_json_and_nesting(self):
        for body in (b'\xff', b'{', b'[]', b'null', b'{"id":1,"result":1}', b'['*2000+b']'*2000):
            with self.subTest(body=body[:40]), self.assertRaises(s.EvidenceError):
                self.call(body)

    def test_response_bound(self):
        with self.assertRaisesRegex(s.EvidenceError, 'size limit'):
            self.call(b' '*4_000_001)

    def test_sequence_and_headers(self):
        rpc = s.RPC(s.RPC_URL)
        opener = MemoryOpener(b'{"jsonrpc":"2.0","id":1,"result":"0x1"}')
        rpc.opener = opener
        rpc.call('eth_chainId', [])
        request, timeout = opener.requests[0]
        self.assertEqual(json.loads(request.data), {'jsonrpc':'2.0','id':1,'method':'eth_chainId','params':[]})
        self.assertIn('Pepeolithic', request.get_header('User-agent'))
        self.assertEqual(timeout, 20)
        with self.assertRaises(s.EvidenceError):
            rpc.call('eth_chainId', [])  # a stale ID on the next request

    def test_public_reads_only(self):
        rpc = s.RPC(s.RPC_URL)
        rpc.opener = MemoryOpener(b'')
        for method in ('eth_sendRawTransaction', 'eth_accounts', 'personal_sign', 'eth_sendTransaction'):
            with self.subTest(method=method), self.assertRaises(s.EvidenceError):
                rpc.call(method, [])
        self.assertEqual(rpc.opener.requests, [])

    def test_url_validation(self):
        for url in ('file:///etc/passwd', 'https://', 'https://user:pass@example.com',
                    'https://example.com/#fragment', 'https://example.com:bad',
                    'https://example.com:0', 'https://example.com/\n', None):
            with self.subTest(url=url), self.assertRaises(s.EvidenceError):
                s.RPC(url)

    def test_no_proxy_discovery(self):
        with patch.object(s.urllib.request, 'getproxies', side_effect=AssertionError('proxy environment read')):
            rpc = s.RPC(s.RPC_URL)
        self.assertFalse(any(isinstance(h, s.urllib.request.ProxyHandler) and h.proxies
                             for h in rpc.opener.handlers))

    def test_actual_http_redirect_refused(self):
        paths = []
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                paths.append(self.path)
                self.send_response(307)
                self.send_header('Location', '/redirect-target')
                self.end_headers()
            def do_GET(self):
                paths.append(self.path)
                self.send_response(200)
                self.end_headers()
            def log_message(self, *args):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            rpc = s.RPC('http://127.0.0.1:'+str(server.server_port)+'/original')
            with self.assertRaises(s.EvidenceError):
                rpc.call('eth_chainId', [])
            self.assertEqual(paths, ['/original'])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main(verbosity=2)
