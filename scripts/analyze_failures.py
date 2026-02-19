"""Analyse test failures from test result files."""

import re
import sys


def parse_test_output(filepath):
    """Parse pytest output to count F/E markers per test file."""
    try:
        content = open(filepath, encoding="utf-8").read()
    except FileNotFoundError:
        return {}

    lines = content.split("\n")
    results = {}
    current_file = None

    for line in lines:
        # Match test file lines like: tests\path\test_file.py .F..EF [xx%]
        m = re.match(r"^(tests[\\/][^\s]+\.py)\s+([\.\sFEsxX]+)\s+\[", line)
        if m:
            current_file = m.group(1).replace("/", "\\")
            markers = m.group(2).strip()
            if current_file not in results:
                results[current_file] = {"F": 0, "E": 0, "pass": 0, "skip": 0, "total": 0}
            for c in markers:
                if c == "F":
                    results[current_file]["F"] += 1
                elif c == "E":
                    results[current_file]["E"] += 1
                elif c == ".":
                    results[current_file]["pass"] += 1
                elif c in ("s", "x", "X"):
                    results[current_file]["skip"] += 1
            results[current_file]["total"] += len([c for c in markers if c in ".FEsxX"])
            continue

        # Continuation lines (only markers + percentage)
        m2 = re.match(r"^([\.FEsxX]+)\s+\[", line.strip())
        if m2 and current_file:
            markers = m2.group(1)
            for c in markers:
                if c == "F":
                    results[current_file]["F"] += 1
                elif c == "E":
                    results[current_file]["E"] += 1
                elif c == ".":
                    results[current_file]["pass"] += 1
                elif c in ("s", "x", "X"):
                    results[current_file]["skip"] += 1
            results[current_file]["total"] += len([c for c in markers if c in ".FEsxX"])

    return results


def main():
    files = ["test_summary.txt", "test_run_result.txt"]

    for filepath in files:
        results = parse_test_output(filepath)
        if not results:
            print(f"\n--- {filepath}: NOT FOUND ---")
            continue

        failed = {k: v for k, v in results.items() if v["F"] > 0 or v["E"] > 0}
        total_f = sum(v["F"] for v in failed.values())
        total_e = sum(v["E"] for v in failed.values())
        total_tests = sum(v["total"] for v in results.values())
        total_pass = sum(v["pass"] for v in results.values())

        print(f"\n{'='*80}")
        print(f"FILE: {filepath}")
        print(
            f"Tests parsed: {total_tests} | Pass: {total_pass} | FAIL: {total_f} | ERROR: {total_e}"
        )
        print(f"Files with failures: {len(failed)}")
        print(f"{'='*80}")

        # Group by module
        modules = {}
        for f, v in sorted(failed.items(), key=lambda x: -(x[1]["F"] + x[1]["E"])):
            # Extract module path
            parts = f.replace("\\", "/").split("/")
            if len(parts) >= 3:
                module = "/".join(parts[1:3])
            else:
                module = parts[1] if len(parts) > 1 else "root"

            if module not in modules:
                modules[module] = {"files": [], "total_f": 0, "total_e": 0}
            modules[module]["files"].append((f, v))
            modules[module]["total_f"] += v["F"]
            modules[module]["total_e"] += v["E"]

        print("\n--- BY MODULE (sorted by total failures) ---")
        for mod, data in sorted(
            modules.items(), key=lambda x: -(x[1]["total_f"] + x[1]["total_e"])
        ):
            total = data["total_f"] + data["total_e"]
            label = f"{data['total_f']}F"
            if data["total_e"] > 0:
                label += f"+{data['total_e']}E"
            print(f"\n  [{label}] {mod}/")
            for f, v in data["files"]:
                fname = f.replace("\\", "/").split("/")[-1]
                fl = f"{v['F']}F"
                if v["E"] > 0:
                    fl += f"+{v['E']}E"
                print(f"      {fl:>8}  {fname}")

        print("\n--- TOP 20 FILES BY FAILURE COUNT ---")
        for i, (f, v) in enumerate(
            sorted(failed.items(), key=lambda x: -(x[1]["F"] + x[1]["E"]))[:20], 1
        ):
            fl = f"{v['F']}F"
            if v["E"] > 0:
                fl += f"+{v['E']}E"
            print(f"  {i:2}. {fl:>8}  {f.replace(chr(92), '/')}")


if __name__ == "__main__":
    main()
