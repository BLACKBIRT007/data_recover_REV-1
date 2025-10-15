# DiskDrill Knockoff

DiskDrill Knockoff is a lightweight, educational data recovery helper inspired by the
popular Disk Drill utility. It provides a simple command-line interface for scanning
raw disk images or binary dumps for common file signatures and optionally carving the
matching content into standalone files.

> **Disclaimer:** This project is intended for educational purposes and should not be
> considered a full-featured replacement for professional data recovery software. Use
> it on copies of data only. Running the tool on a live disk image can take a long time
> and may not recover all lost files.

## Features

- Signature-based scanning for common file types (JPEG, PNG, PDF, ZIP, MP3, SQLite, etc.).
- Human-readable scan reports with byte offsets and estimated file sizes.
- Carve-and-save mode to extract the identified files into a safe destination folder.
- Extensible signature catalog defined in plain Python.

## Installation

The project is self-contained and has no third-party dependencies. To use it inside
this repository, run the module with Python 3.10 or newer:

```bash
python -m diskdrill_knockoff --help
```

To install it as a command-line script, install the project in editable mode:

```bash
pip install -e .
```

This exposes the `diskdrill-knockoff` console entry point.

## Usage

### Scan an image

```bash
python -m diskdrill_knockoff scan path/to/disk-image.dd
```

The command prints a table that lists the discovered file signatures, their offsets,
file type, and estimated size.

### Recover matched files

```bash
python -m diskdrill_knockoff recover path/to/disk-image.dd recovered/
```

By default the `recover` command extracts all matches into the output directory.
Use `--only-types` to filter by file extension or pass specific match identifiers via
`--ids`. Recovered files are named using the pattern `<offset>_<extension>`.

## Limitations

- Signature carving is best effort and does not understand file system metadata.
- Only a limited number of file types are supported out-of-the-box.
- Carving relies on finding a valid footer or a configurable maximum size.
- Very large images may take a long time to scan; consider using the `--limit` option
  to stop after a given number of matches.

## Development

The codebase is intentionally small and easy to modify. Run the unit tests with:

```bash
pytest
```

Feel free to extend the `SIGNATURES` dictionary in `diskdrill_knockoff/signatures.py`
to add support for more file types or more precise end markers.
