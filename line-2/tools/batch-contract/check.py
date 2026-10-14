#!/usr/bin/env python3
"""Validate multiple JSON documents against one offline structural contract."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def engine_module():
    path = Path(__file__).resolve().parent.parent / "json-contract" / "check.py"
    if not path.is_relative_to(Path.cwd().resolve()):
        raise ValueError("run from a workspace containing both tool folders")
    spec = importlib.util.spec_from_file_location("json_contract_engine", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_all(engine, contract, names):
    rows = []
    problems = 0
    unreadable = 0
    for name in names:
        try:
            errors = engine.validate(engine.load(name), contract)
            problems += bool(errors)
            rows.append({"file": name, "valid": not errors, "errors": errors})
        except (ValueError, OSError, RecursionError) as exc:
            unreadable += 1
            rows.append({"file": name, "valid": False, "errors": [], "error": str(exc)})
    report = {
        "valid": problems == 0 and unreadable == 0,
        "summary": {"checked": len(rows), "passed": len(rows) - problems - unreadable,
                    "failed": problems, "unreadable": unreadable},
        "files": rows,
    }
    return report, 2 if unreadable else (1 if problems else 0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", help="contract JSON inside the workspace")
    parser.add_argument("documents", nargs="+", help="JSON files to check, in given order")
    args = parser.parse_args(argv)
    if len(args.documents) > 256:
        print(json.dumps({"error": "at most 256 documents per invocation"}))
        return 2
    try:
        engine = engine_module()
        contract = engine.prepare(engine.load(args.contract))
        report, code = check_all(engine, contract, args.documents)
        print(json.dumps(report, indent=2))
        return code
    except (ValueError, OSError, RecursionError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
