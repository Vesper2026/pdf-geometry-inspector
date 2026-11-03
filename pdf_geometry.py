"""Read-only PDF page geometry. Physical dimensions use 1 pt = 1/72 inch."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import sys
from typing import Any

from pypdf import PdfReader
from pypdf.errors import DependencyError, FileNotDecryptedError, PdfReadError

MM_PER_PT = 25.4 / 72


def number(value: Any) -> float | None:
    """Do not silently turn malformed or non-finite PDF numbers into geometry."""
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def dimensions(width: float, height: float) -> dict[str, Any]:
    return {
        "width_pt": round(width, 6), "height_pt": round(height, 6),
        "width_mm": round(width * MM_PER_PT, 6),
        "height_mm": round(height * MM_PER_PT, 6),
    }


def orientation(width: float, height: float) -> str:
    if math.isclose(width, height, rel_tol=0, abs_tol=1e-6):
        return "square"
    return "landscape" if width > height else "portrait"


def inspect_page(page: Any, index: int) -> dict[str, Any]:
    warnings: list[dict[str, str]] = []

    def warn(code: str, message: str) -> None:
        warnings.append({"code": code, "message": message})

    def box(key: str, fallback: list[float] | None = None) -> dict[str, Any]:
        obj = page.get(key)
        if obj is None:
            if fallback is not None:
                return {"raw": list(fallback), "source": "MediaBox default", "valid": True}
            warn("missing_" + key[1:].lower(), f"{key} is missing and has no usable default.")
            return {"raw": None, "source": "missing", "valid": False}
        if hasattr(obj, "get_object"):
            obj = obj.get_object()
        if not isinstance(obj, (list, tuple)) or len(obj) != 4:
            warn("invalid_" + key[1:].lower(), f"{key} must contain four finite numbers.")
            return {"raw": str(obj), "source": "PDF", "valid": False}
        values = [number(v) for v in obj]
        if any(v is None for v in values):
            warn("invalid_" + key[1:].lower(), f"{key} contains a non-finite or invalid coordinate.")
            return {"raw": [str(v) for v in obj], "source": "PDF", "valid": False}
        valid = values[2] > values[0] and values[3] > values[1]
        if not valid:
            warn("non_positive_" + key[1:].lower(), f"{key} has non-positive width or height; coordinates are not reordered.")
        return {"raw": values, "source": "PDF", "valid": valid}

    media = box("/MediaBox")
    crop = box("/CropBox", media["raw"] if media["valid"] else None)
    unit_obj = page.get("/UserUnit", 1)
    unit = number(unit_obj)
    if unit is None or unit <= 0:
        warn("invalid_user_unit", "UserUnit must be positive and finite; physical dimensions are unknown.")
        unit = None
    elif unit > 75000:
        warn("user_unit_out_of_range", "UserUnit exceeds the PDF specification maximum of 75000.")
    rotate_obj = page.get("/Rotate", 0)
    rotation = number(rotate_obj)
    normalized = rotation % 360 if rotation is not None else None
    orthogonal = normalized is not None and normalized % 90 == 0
    if not orthogonal:
        warn("non_90_rotation", "Rotate is not a finite multiple of 90; displayed dimensions and orientation are unknown.")

    visible_box = None
    visible_dimensions = None
    displayed_dimensions = None
    direction = "unknown"
    if media["valid"] and crop["valid"]:
        m, c = media["raw"], crop["raw"]
        if c[0] < m[0] or c[1] < m[1] or c[2] > m[2] or c[3] > m[3]:
            warn("crop_outside_media", "CropBox extends outside MediaBox; visible geometry uses their intersection.")
        intersection = [max(m[0], c[0]), max(m[1], c[1]), min(m[2], c[2]), min(m[3], c[3])]
        if intersection[2] <= intersection[0] or intersection[3] <= intersection[1]:
            warn("empty_intersection", "MediaBox and CropBox have no positive-area intersection.")
        else:
            visible_box = intersection
            if unit is not None:
                width = (intersection[2] - intersection[0]) * unit
                height = (intersection[3] - intersection[1]) * unit
                if not math.isfinite(width) or not math.isfinite(height):
                    warn("dimension_overflow", "Scaled dimensions exceed finite numeric range.")
                else:
                    visible_dimensions = dimensions(width, height)
                    if orthogonal:
                        if normalized in (90, 270):
                            width, height = height, width
                        displayed_dimensions = dimensions(width, height)
                        direction = orientation(width, height)
    return {
        "page": index, "media_box": media, "crop_box": crop,
        "user_unit": unit, "user_unit_raw": str(unit_obj) if unit is None else unit,
        "rotation_degrees": rotation,
        "rotation_raw": str(rotate_obj) if rotation is None else rotation,
        "normalized_rotation_degrees": normalized,
        "visible_box_raw": visible_box,
        "visible_dimensions": visible_dimensions,
        "displayed_dimensions": displayed_dimensions,
        "orientation": direction, "warnings": warnings,
    }


def size_groups(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[float, float], dict[str, Any]] = {}
    for page in pages:
        size = page["displayed_dimensions"]
        if size is None:
            continue
        key = (round(size["width_pt"], 3), round(size["height_pt"], 3))
        if key not in groups:
            groups[key] = {**dimensions(*key), "orientation": page["orientation"], "pages": []}
        groups[key]["pages"].append(page["page"])
    return list(groups.values())


def inspect_pdf(path: str | Path) -> dict[str, Any]:
    """Read bytes only; no PDF writer, password input, or explicit decryption."""
    source = Path(path).resolve()
    with source.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _sha256(stream)
        stream.seek(0)
        report: dict[str, Any] = {
            "schema_version": 1, "input_file": str(source), "sha256": digest,
            "status": "ok", "pdf_header": None,
            "encrypted": None,
            "access": "readable", "metadata": None, "page_count": None,
            "pages": [], "size_groups": [], "ungrouped_pages": [], "warnings": [],
            "geometry_policy": {
                "visible_area": "positive-area intersection of MediaBox and CropBox",
                "coordinate_unit": "raw PDF default user-space units",
                "physical_unit": "pt = raw unit * UserUnit; mm = pt * 25.4 / 72",
                "displayed_dimensions": "swap width/height for 90 or 270 degrees; unknown for non-90-degree rotation",
                "size_grouping": "displayed width and height rounded to 0.001 pt; orientation-sensitive; unknown sizes excluded",
            },
        }
        try:
            reader = PdfReader(stream, strict=False)
        except (DependencyError, NotImplementedError) as exc:
            report.update(status="restricted", encrypted=True, access="encryption_unsupported")
            report["warnings"].append({"code": "encryption_unsupported", "message": str(exc)})
            return report
        report.update(pdf_header=reader.pdf_header, encrypted=reader.is_encrypted)
        try:
            count = len(reader.pages)
            metadata = reader.metadata
            if metadata is not None:
                report["metadata"] = {str(k): str(v) for k, v in metadata.items()}
            report["page_count"] = count
            report["pages"] = [inspect_page(page, i) for i, page in enumerate(reader.pages, 1)]
            report["size_groups"] = size_groups(report["pages"])
            report["ungrouped_pages"] = [p["page"] for p in report["pages"] if p["displayed_dimensions"] is None]
            if reader.is_encrypted:
                report["access"] = "readable_without_supplied_password"
        except (FileNotDecryptedError, DependencyError, NotImplementedError) as exc:
            password_required = isinstance(exc, FileNotDecryptedError)
            report.update(status="restricted", access="password_required" if password_required else "encryption_unsupported",
                          metadata=None, page_count=None, pages=[], size_groups=[], ungrouped_pages=[])
            report["warnings"].append({
                "code": "encrypted_restricted" if password_required else "encryption_unsupported",
                "message": "Encrypted document cannot be read without a password. No password is accepted or supplied by this tool." if password_required else str(exc),
            })
        return report


def _sha256(stream: Any) -> str:
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def markdown(report: dict[str, Any]) -> str:
    def safe(value: Any) -> str:
        return html.escape(str(value), quote=False).replace("\\", "\\\\").replace("|", "\\|").replace("\r", " ").replace("\n", " ").replace("`", "\\`")

    def size(value: dict[str, Any] | None) -> str:
        if value is None:
            return "unknown"
        return f"{value['width_pt']:.3f} × {value['height_pt']:.3f} pt / {value['width_mm']:.3f} × {value['height_mm']:.3f} mm"

    lines = ["# PDF geometry inspection", "", f"- Input: {safe(report['input_file'])}",
             f"- SHA-256: {report['sha256']}", f"- Status: {report['status']}",
             f"- PDF header: {safe(report['pdf_header'])}",
             f"- Encrypted: {str(report['encrypted']).lower()}",
             f"- Access: {report['access']}", f"- Pages: {report['page_count']}", "",
             "## Geometry rules", ""]
    lines.extend(f"- {safe(k)}: {safe(v)}" for k, v in report["geometry_policy"].items())
    lines.extend(["", "## Document metadata", ""])
    if report["metadata"] is None:
        lines.append("Unavailable (absent or restricted).")
    else:
        lines.extend(f"- {safe(k)}: {safe(v)}" for k, v in report["metadata"].items())
        if not report["metadata"]:
            lines.append("Empty metadata dictionary.")
    lines.extend(["", "## Pages", "", "| Page | MediaBox raw | CropBox raw | UserUnit | Rotate | Visible raw | Effective size before rotation | Displayed size | Orientation | Warnings |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"])
    for page in report["pages"]:
        cells = [page["page"], page["media_box"]["raw"], page["crop_box"]["raw"], page["user_unit_raw"], page["rotation_raw"], page["visible_box_raw"], size(page["visible_dimensions"]), size(page["displayed_dimensions"]), page["orientation"], "; ".join(w["code"] + ": " + w["message"] for w in page["warnings"])]
        lines.append("| " + " | ".join(safe(c) for c in cells) + " |")
    lines.extend(["", "## Size groups", ""])
    for group in report["size_groups"]:
        lines.append(f"- {size(group)} ({group['orientation']}): pages {', '.join(map(str, group['pages']))}")
    if not report["size_groups"]:
        lines.append("No known displayed sizes.")
    if report.get("ungrouped_pages"):
        lines.append(f"- Unknown size, excluded: {report['ungrouped_pages']}")
    if report["warnings"]:
        lines.extend(["", "## Document warnings", ""])
        lines.extend(f"- {safe(w['code'])}: {safe(w['message'])}" for w in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect local PDF geometry without changing the PDF. No password option.")
    parser.add_argument("pdf", type=Path, help="Local PDF file")
    parser.add_argument("--output", type=Path, default=Path("inspection"), help="Report directory (default: inspection)")
    args = parser.parse_args(argv)
    try:
        targets = [args.output / "inspection.json", args.output / "inspection.md"]
        if any(target.resolve() == args.pdf.resolve() for target in targets):
            raise ValueError("Report destination must not overwrite the input file.")
        report = inspect_pdf(args.pdf)
        args.output.mkdir(parents=True, exist_ok=True)
        targets[0].write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        targets[1].write_text(markdown(report), encoding="utf-8")
    except (OSError, ValueError, PdfReadError) as exc:
        print(f"Inspection failed: {exc}", file=sys.stderr)
        return 1
    print(f"Status: {report['status']}; encrypted: {str(report['encrypted']).lower()}; pages: {report['page_count']}")
    print(f"Size groups: {len(report['size_groups'])}; page warnings: {sum(len(p['warnings']) for p in report['pages'])}")
    print(f"JSON: {targets[0].resolve()}")
    print(f"Markdown: {targets[1].resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
