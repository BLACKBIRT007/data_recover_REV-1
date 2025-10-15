"""Signature-based scanner for raw disk images."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence
import mmap

from .signatures import SIGNATURES, Signature


@dataclass
class ScanMatch:
    """Describes a recovered signature match within an image."""

    id: int
    offset: int
    size: int
    signature: Signature

    def filename(self) -> str:
        return f"{self.offset:012d}.{self.signature.extension}"

    def to_row(self) -> tuple[str, str, str, str]:
        return (
            str(self.id),
            f"0x{self.offset:08X}",
            self.signature.extension,
            human_readable_size(self.size),
        )


def human_readable_size(size: int) -> str:
    units = ["B", "KiB", "MiB", "GiB"]
    value = float(size)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TiB"


def scan_image(
    image_path: str | Path,
    signatures: Sequence[Signature] = SIGNATURES,
    limit: int | None = None,
) -> List[ScanMatch]:
    """Scan *image_path* for known file signatures.

    Parameters
    ----------
    image_path:
        Path to a raw disk image or binary blob.
    signatures:
        Iterable of :class:`Signature` definitions.
    limit:
        Optional cap on the number of matches to return.
    """

    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(path)

    matches: List[ScanMatch] = []
    with path.open("rb") as fh, mmap.mmap(fh.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
        for sig in signatures:
            start = 0
            while True:
                idx = mm.find(sig.header, start)
                if idx == -1:
                    break

                end = _find_end(mm, idx + len(sig.header), sig)
                matches.append(
                    ScanMatch(
                        id=len(matches) + 1,
                        offset=idx,
                        size=end - idx,
                        signature=sig,
                    )
                )

                if limit is not None and len(matches) >= limit:
                    return matches
                start = idx + len(sig.header)

    matches.sort(key=lambda match: match.offset)
    for new_id, match in enumerate(matches, start=1):
        match.id = new_id
    return matches


def _find_end(mm: mmap.mmap, search_from: int, signature: Signature) -> int:
    if signature.footer:
        idx = mm.find(signature.footer, search_from)
        if idx != -1:
            return idx + len(signature.footer)

    max_end = search_from + signature.max_size
    if max_end > mm.size():
        max_end = mm.size()
    return max_end
