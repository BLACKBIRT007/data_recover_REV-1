"""Carve file signatures out of raw binary images."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List
import mmap

from .scanner import ScanMatch


class RecoveryError(RuntimeError):
    """Raised when the recovery process fails."""


def recover_matches(
    image_path: str | Path,
    matches: Iterable[ScanMatch],
    output_dir: str | Path,
    ids: set[int] | None = None,
    only_extensions: set[str] | None = None,
    overwrite: bool = False,
) -> List[Path]:
    """Recover the selected *matches* to *output_dir*.

    Parameters
    ----------
    image_path:
        Source image that will be read.
    matches:
        Sequence of matches, typically as returned by :func:`scan_image`.
    output_dir:
        Directory where the carved files should be written.
    ids:
        Optional subset of match identifiers to recover.
    only_extensions:
        Optional filter by file extension.
    overwrite:
        When ``False`` (default) existing files are skipped.
    """

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(path)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    selected = _filter_matches(matches, ids=ids, only_extensions=only_extensions)

    written: List[Path] = []
    with path.open("rb") as fh, mmap.mmap(fh.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
        size = mm.size()
        for match in selected:
            start = match.offset
            end = match.offset + match.size
            if end > size:
                end = size

            data = mm[start:end]
            if not data:
                continue

            output_file = output_path / match.filename()
            if output_file.exists() and not overwrite:
                continue

            output_file.write_bytes(data)
            written.append(output_file)
    return written


def _filter_matches(
    matches: Iterable[ScanMatch],
    ids: set[int] | None,
    only_extensions: set[str] | None,
) -> List[ScanMatch]:
    filtered: List[ScanMatch] = []
    for match in matches:
        if ids is not None and match.id not in ids:
            continue
        if only_extensions is not None and match.signature.extension not in only_extensions:
            continue
        filtered.append(match)
    return filtered
