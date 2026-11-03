"""Generate real synthetic PDFs with pypdf, including deliberately invalid geometry."""
from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject, DecodedStreamObject, DictionaryObject, FloatObject,
    NameObject, NumberObject,
)

A4_WIDTH = 210 * 72 / 25.4
A4_HEIGHT = 297 * 72 / 25.4


def rectangle(values: list[float]) -> ArrayObject:
    return ArrayObject([FloatObject(v) for v in values])


def add_page(writer: PdfWriter, width: float, height: float, label: str):
    page = writer.add_blank_page(width=width, height=height)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({
            NameObject("/F1"): DictionaryObject({
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            })
        })
    })
    content = DecodedStreamObject()
    content.set_data(f"q 0.5 w 36 36 {width - 72:.3f} {height - 72:.3f} re S Q\nBT /F1 12 Tf 48 60 Td ({label}) Tj ET\n".encode("ascii"))
    page[NameObject("/Contents")] = content
    return page


def generate_samples(output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    writer.pdf_header = "%PDF-1.7"
    writer.add_metadata({"/Title": "Synthetic PDF geometry cases", "/Author": "PDF Geometry Inspector examples"})
    add_page(writer, A4_WIDTH, A4_HEIGHT, "1 A4 portrait")
    page = add_page(writer, A4_WIDTH, A4_HEIGHT, "2 A4 rotated 90")
    page[NameObject("/Rotate")] = NumberObject(90)
    page = add_page(writer, 612, 792, "3 Letter cropped to 7 x 10 inches")
    page[NameObject("/CropBox")] = rectangle([54, 36, 558, 756])
    page = add_page(writer, 200, 300, "4 UserUnit 2")
    page[NameObject("/UserUnit")] = FloatObject(2)
    page = add_page(writer, 612, 792, "5 CropBox outside MediaBox")
    page[NameObject("/CropBox")] = rectangle([-20, -10, 700, 900])
    page = add_page(writer, 612, 792, "6 Empty intersection")
    page[NameObject("/CropBox")] = rectangle([700, 800, 900, 1000])
    page = add_page(writer, 612, 792, "7 Unsupported rotation 45")
    page[NameObject("/Rotate")] = NumberObject(45)
    page = add_page(writer, 612, 792, "8 Zero-width CropBox")
    page[NameObject("/CropBox")] = rectangle([100, 0, 100, 792])
    page = add_page(writer, 612, 792, "9 Reversed MediaBox")
    page[NameObject("/MediaBox")] = rectangle([612, 0, 0, 792])
    page = add_page(writer, A4_WIDTH, A4_HEIGHT, "10 A4 rotated 270")
    page[NameObject("/Rotate")] = NumberObject(270)
    geometry_cases = output / "geometry_cases.pdf"
    writer.write(geometry_cases)

    public = PdfWriter()
    public.add_metadata({"/Title": "Three-page geometry sample"})
    add_page(public, 595.276, 841.89, "1 A4 portrait")
    page = add_page(public, 595.276, 841.89, "2 A4 rotated 90")
    page[NameObject("/Rotate")] = NumberObject(90)
    page = add_page(public, 612, 792, "3 Letter cropped to 8 x 10 inches")
    page[NameObject("/CropBox")] = rectangle([18, 36, 594, 756])
    sample = output / "sample.pdf"
    public.write(sample)

    plain = PdfWriter()
    add_page(plain, A4_WIDTH, A4_HEIGHT, "No document metadata")
    plain.metadata = None
    no_metadata = output / "no_metadata.pdf"
    plain.write(no_metadata)

    locked = PdfWriter()
    add_page(locked, 612, 792, "Encrypted synthetic fixture")
    locked.encrypt("synthetic-fixture-only")
    encrypted = output / "encrypted.pdf"
    locked.write(encrypted)

    empty = PdfWriter()
    add_page(empty, 612, 792, "Empty-password synthetic fixture")
    empty.encrypt("", owner_password="synthetic-owner-only")
    empty_password = output / "empty_password.pdf"
    empty.write(empty_password)
    return [sample, geometry_cases, no_metadata, encrypted, empty_password]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    for path in generate_samples(args.output):
        print(path.resolve())


if __name__ == "__main__":
    main()
