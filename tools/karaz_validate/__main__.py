"""Command line: python -m tools.karaz_validate [--root PATH] [--format text|json].

Exit codes: 0 when there is no ERROR, 1 when there is any ERROR, 2 when the
validator itself cannot run. WARNING and INFO never cause a failure, and there
is no option that turns them into one.
"""

from __future__ import annotations

import argparse
import sys

from . import RootError, validate
from .loader import MAX_FILE_BYTES


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.karaz_validate",
        description="Read-only structural validation of the KARAZ repository.",
        epilog=f"Files larger than {MAX_FILE_BYTES // 1024} KiB are rejected (KZ-L001). "
               "WARNING and INFO never cause a non-zero exit.",
    )
    parser.add_argument("--root", default=".", help="repository root to check (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    args = parser.parse_args(argv)  # argparse itself exits with 2 on a usage error
    try:
        report = validate(args.root)
    except RootError as exc:
        print(f"validator cannot run: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # a crash must never look like a pass
        print(f"validator cannot run: internal error: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(report.render_json() if args.format == "json" else report.render_text())
    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
