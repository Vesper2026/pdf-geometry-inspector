# PDF Geometry Inspector

[繁體中文](README.zh-Hant.md) · [Website](https://pdf.vesperai.space/en/)

Read local PDF page geometry and metadata without modifying the source. Inspect MediaBox, CropBox intersection, UserUnit and quarter-turn rotation.

## Run

Requires Python 3.10+. Clone this repository, then work from its root:

```sh
git clone https://github.com/Vesper2026/pdf-geometry-inspector.git
cd pdf-geometry-inspector
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe examples/generate_sample.py
.venv/Scripts/python.exe pdf_geometry.py examples/sample.pdf --output examples/output
```

On macOS/Linux replace `.venv/Scripts/python.exe` with `.venv/bin/python`. The pinned dependency is listed in requirements.txt; retain its BSD-3-Clause license when redistributing it.

## Input and actual example output

```text
Three synthetic blank pages: A4; rotated A4; Letter with CropBox [18,36,594,756].
```

The bundled fixture, not just the abbreviated illustration above, produces:

```text
examples/output/inspection.json
examples/output/inspection.md
```

Reports raw boxes, effective visible geometry, points/millimetres, rotation, orientation, dimension groups and metadata. The Letter crop has 576 × 720 points of visible area at UserUnit 1, or 203.2 × 254 mm. UserUnit scales coordinate dimensions; 90/270-degree rotations swap width and height. Out-of-media crops, nonpositive rectangles, empty intersections and unsupported rotations are reported for review, not silently repaired. Restricted encrypted documents do not receive invented page details.

## Tests

```sh
.venv/Scripts/python.exe -m unittest discover -p "test_*.py"
```

Run the real synthetic-PDF tests in test_geometry.py; they cover page boxes, scale, rotation, restricted documents and unchanged input bytes.

## Limits and privacy

Read-only geometry inspection is not rendering, OCR, repair, signature validation, secure redaction, provenance authentication or complete PDF conformance validation. Mixed page sizes can be intentional. Metadata can be absent or forged. No password cracking or document upload. Installing pypdf contacts your package index; pypdf is a third-party BSD-3-Clause dependency, not bundled private product code.

## Build this repository's independent bilingual site

```sh
python site/build.py
python -m http.server 8090 --directory docs
```

Open http://localhost:8090/en/ or /zh-Hant/. The source lives in `site/`, output in `docs/`, and examples are copied to `docs/downloads/`. The site has two original articles per language, its own hostname/canonical/sitemap/robots/CNAME, and no analytics or upload form. 

## Useful tools

[KomoPDF](https://komopdf.com/) can be used alongside this tool. KolmoPDF's cloud service uploads documents; these open-source local CLIs do not replace its proprietary parser.

## License

MIT for this code, authored fixtures, documentation and static-site sources; see LICENSE. Third-party dependencies keep their own licenses.
