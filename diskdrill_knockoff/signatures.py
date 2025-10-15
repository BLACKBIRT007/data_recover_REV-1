"""Catalog of file signatures used by the scanner."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Signature:
    name: str
    extension: str
    header: bytes
    footer: Optional[bytes] = None
    max_size: int = 8 * 1024 * 1024  # 8 MiB default safety cap
    description: str | None = None


SIGNATURES: tuple[Signature, ...] = (
    Signature(
        name="JPEG image",
        extension="jpg",
        header=b"\xFF\xD8\xFF",
        footer=b"\xFF\xD9",
        max_size=25 * 1024 * 1024,
        description="Common digital photo format",
    ),
    Signature(
        name="Portable Network Graphics",
        extension="png",
        header=b"\x89PNG\r\n\x1a\n",
        footer=b"IEND\xaeB`\x82",
        max_size=20 * 1024 * 1024,
    ),
    Signature(
        name="PDF document",
        extension="pdf",
        header=b"%PDF-",
        footer=b"%%EOF",
        max_size=40 * 1024 * 1024,
    ),
    Signature(
        name="ZIP archive",
        extension="zip",
        header=b"PK\x03\x04",
        footer=b"PK\x05\x06",
        max_size=100 * 1024 * 1024,
    ),
    Signature(
        name="MP3 audio",
        extension="mp3",
        header=b"ID3",
        max_size=20 * 1024 * 1024,
    ),
    Signature(
        name="SQLite database",
        extension="sqlite",
        header=b"SQLite format 3\x00",
        max_size=50 * 1024 * 1024,
    ),
    Signature(
        name="GIF image",
        extension="gif",
        header=b"GIF8",
        footer=b";",
        max_size=10 * 1024 * 1024,
    ),
    Signature(
        name="Portable Executable",
        extension="exe",
        header=b"MZ",
        max_size=50 * 1024 * 1024,
    ),
)
