#!/usr/bin/env python3
"""Render PDF pages or crop complete figures with normalized coordinates and source records."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_pages(value: str, count: int) -> list[int]:
    """Expand and deduplicate one-based page numbers and ranges."""
    result = []
    for piece in value.split(","):
        match = re.fullmatch(r"\s*([1-9][0-9]*)(?:-([1-9][0-9]*))?\s*", piece)
        if not match:
            raise ValueError("Use one-based page numbers, for example: 1,3-5.")
        first = int(match.group(1))
        last = int(match.group(2) or first)
        if first > last or last > count:
            raise ValueError(f"Pages must be within 1-{count}, with ascending ranges.")
        result.extend(range(first, last + 1))
    return list(dict.fromkeys(result))


def parse_box(value: str) -> tuple[float, float, float, float]:
    try:
        box = tuple(float(part) for part in value.split(","))
    except ValueError as error:
        raise ValueError("The crop box must contain four numbers.") from error
    if len(box) != 4 or not all(math.isfinite(n) for n in box):
        raise ValueError("The crop box must contain four finite values.")
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ValueError("The box requires 0 <= left < right <= 1 and 0 <= top < bottom <= 1.")
    return box


def load_pdf(path: Path):
    try:
        import pymupdf
    except ImportError as error:
        raise RuntimeError("PyMuPDF is missing; install requirements.txt.") from error
    if path.suffix.lower() != ".pdf":
        raise ValueError("The input file must have a .pdf extension.")
    document = pymupdf.open(path)
    if not document.is_pdf or document.needs_pass or document.page_count == 0:
        document.close()
        raise ValueError("The PDF must open without a password and contain at least one page.")
    return document


def render_page(page, dpi: int):
    try:
        import pymupdf
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("PyMuPDF or Pillow is missing; install requirements.txt.") from error
    if not 72 <= dpi <= 600:
        raise ValueError("dpi must be within 72-600.")
    pixels = page.rect.width * page.rect.height * (dpi / 72) ** 2
    if pixels > 40_000_000:
        raise ValueError("Rendering exceeds 40 million pixels; reduce dpi.")
    pixmap = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def ensure_new(paths: list[Path]) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError("Output exists; use a new directory or figure ID: " + ", ".join(existing))


def save_png(image, path: Path, dpi: int) -> None:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", dpi=(dpi, dpi))
    with path.open("xb") as stream:
        stream.write(buffer.getvalue())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def execute(args: argparse.Namespace) -> list[Path]:
    source = args.pdf.expanduser().resolve(strict=True)
    output = args.out.expanduser().resolve()
    if not 72 <= args.dpi <= 600:
        raise ValueError("dpi must be within 72-600.")
    with load_pdf(source) as document:
        if args.command == "render":
            pages = parse_pages(args.pages, document.page_count)
            paths = [output / f"page-{number:03d}.png" for number in pages]
            ensure_new(paths)
            output.mkdir(parents=True, exist_ok=True)
            for number, path in zip(pages, paths):
                save_png(render_page(document[number - 1], args.dpi), path, args.dpi)
            return paths

        if not re.fullmatch(r"P[0-9]{2,}-Fig[0-9A-Za-z][0-9A-Za-z._-]*", args.figure_id):
            raise ValueError("Use a figure ID such as P01-Fig2; letters, digits, dots, underscores and hyphens only.")
        if not 1 <= args.page <= document.page_count:
            raise ValueError(f"The page must be within 1-{document.page_count}.")
        box = parse_box(args.box)
        image_path = output / f"{args.figure_id}.png"
        record_path = output / f"{args.figure_id}.json"
        ensure_new([image_path, record_path])
        image = render_page(document[args.page - 1], args.dpi)
        left, top, right, bottom = box
        pixel_box = (
            math.floor(left * image.width), math.floor(top * image.height),
            math.ceil(right * image.width), math.ceil(bottom * image.height),
        )
        cropped = image.crop(pixel_box)
        record = {
            "source_pdf": str(source),
            "pdf_sha256": sha256(source),
            "figure_id": args.figure_id,
            "page_1_based": args.page,
            "page_rotation": document[args.page - 1].rotation,
            "coordinate_system": "Normalized coordinates from the rendered page's top-left, including page rotation",
            "box_normalized": list(box),
            "box_pixels": list(pixel_box),
            "dpi": args.dpi,
            "output_size_px": [cropped.width, cropped.height],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "visually_verified": False,
            "caption": None,
        }
        output.mkdir(parents=True, exist_ok=True)
        save_png(cropped, image_path, args.dpi)
        with record_path.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        return [image_path, record_path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("render", "crop"):
        command = subparsers.add_parser(name)
        command.add_argument("--pdf", required=True, type=Path)
        command.add_argument("--out", required=True, type=Path)
        command.add_argument("--dpi", type=int, default=180)
        if name == "render":
            command.add_argument("--pages", required=True, help="For example: 1,3-5")
        else:
            command.add_argument("--page", required=True, type=int)
            command.add_argument("--box", required=True, help="Normalized left,top,right,bottom")
            command.add_argument("--figure-id", required=True)
    args = parser.parse_args()
    try:
        for path in execute(args):
            print(path)
    except Exception as error:
        parser.exit(1, f"PDF processing failed: {error}\n")


if __name__ == "__main__":
    main()
