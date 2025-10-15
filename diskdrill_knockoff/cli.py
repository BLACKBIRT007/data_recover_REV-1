"""Command line interface for the DiskDrill knockoff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

from .carver import recover_matches
from .scanner import ScanMatch, human_readable_size, scan_image
from .signatures import SIGNATURES


def main(argv: List[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return _cmd_scan(args)
    if args.command == "recover":
        return _cmd_recover(args)
    parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Educational Disk Drill style scanner")
    sub = parser.add_subparsers(dest="command")

    scan_parser = sub.add_parser("scan", help="scan an image for known signatures")
    scan_parser.add_argument("image", help="path to the disk image to scan")
    scan_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="maximum number of matches to report",
    )
    scan_parser.add_argument(
        "--json",
        action="store_true",
        help="emit machine readable JSON output",
    )

    recover_parser = sub.add_parser("recover", help="recover carved files from an image")
    recover_parser.add_argument("image", help="path to the disk image to scan")
    recover_parser.add_argument("output", help="directory where recovered files are written")
    recover_parser.add_argument(
        "--ids",
        nargs="+",
        type=int,
        default=None,
        help="recover only the matches with the given identifiers",
    )
    recover_parser.add_argument(
        "--only-types",
        nargs="+",
        default=None,
        help="recover only files with the given extensions (e.g. jpg png)",
    )
    recover_parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="maximum number of matches to consider",
    )
    recover_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing files in the output directory",
    )

    return parser


def _cmd_scan(args: argparse.Namespace) -> int:
    matches = scan_image(args.image, SIGNATURES, limit=args.limit)
    if args.json:
        json.dump([_match_to_json(match) for match in matches], fp=sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    if not matches:
        print("No signatures discovered.")
        return 0

    print(f"Found {len(matches)} potential files in {args.image} (size {human_readable_size(Path(args.image).stat().st_size)})")
    headers = ["ID", "Offset", "Type", "Size", "Description"]
    rows = [match.to_row() + (match.signature.description or match.signature.name,) for match in matches]
    print(_format_table(headers, rows))
    return 0


def _cmd_recover(args: argparse.Namespace) -> int:
    matches = scan_image(args.image, SIGNATURES, limit=args.limit)
    id_filter = set(args.ids) if args.ids else None
    ext_filter = set(args.only_types) if args.only_types else None

    written = recover_matches(
        args.image,
        matches,
        args.output,
        ids=id_filter,
        only_extensions=ext_filter,
        overwrite=args.overwrite,
    )

    if written:
        print(f"Recovered {len(written)} file(s) into {args.output}")
        for path in written:
            print(f" - {path.name}")
    else:
        print("No files written. Check your filters or ensure the image contains known signatures.")
    return 0


def _match_to_json(match: ScanMatch) -> dict[str, object]:
    return {
        "id": match.id,
        "offset": match.offset,
        "size": match.size,
        "extension": match.signature.extension,
        "type": match.signature.name,
        "description": match.signature.description,
    }


def _format_table(headers: List[str], rows: Iterable[Iterable[str]]) -> str:
    cols = list(zip(*([headers] + [list(row) for row in rows])))
    widths = [max(len(str(item)) for item in col) for col in cols]

    def format_row(items: Iterable[str]) -> str:
        return " | ".join(str(item).ljust(width) for item, width in zip(items, widths))

    divider = "-+-".join("-" * width for width in widths)
    lines = [format_row(headers), divider]
    for row in rows:
        lines.append(format_row(row))
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
