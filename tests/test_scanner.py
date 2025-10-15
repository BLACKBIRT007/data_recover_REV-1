from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diskdrill_knockoff.carver import recover_matches
from diskdrill_knockoff.scanner import scan_image


@pytest.fixture()
def sample_image(tmp_path: Path) -> Path:
    data = bytearray()
    data += b"garbage"
    # JPEG
    data += b"\xFF\xD8\xFF"
    data += b"JPEGDATA"
    data += b"\xFF\xD9"
    # PDF without footer should cap at max size (40 MiB) but we limit by file length
    data += b"%PDF-1.7\nbody"
    path = tmp_path / "image.bin"
    path.write_bytes(data)
    return path


def test_scan_finds_signatures(sample_image: Path):
    matches = scan_image(sample_image)
    assert [m.signature.extension for m in matches] == ["jpg", "pdf"]
    jpg = matches[0]
    assert jpg.offset == len(b"garbage")
    assert jpg.size == len(b"\xFF\xD8\xFF" + b"JPEGDATA" + b"\xFF\xD9")


def test_recover_writes_files(tmp_path: Path, sample_image: Path):
    matches = scan_image(sample_image)
    out_dir = tmp_path / "recovered"
    written = recover_matches(sample_image, matches, out_dir)
    assert len(written) == 2
    assert all(path.exists() for path in written)
