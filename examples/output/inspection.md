# PDF geometry inspection

- Input: D:\\workdata\\webprojects\\seo\\accounts\\Vesper2026\\pdf-geometry-inspector\\examples\\sample.pdf
- SHA-256: 04604996ef9b0cda27da651e8cbfc752826541488a7099809aebbed6c7c047ef
- Status: ok
- PDF header: %PDF-1.3
- Encrypted: false
- Access: readable
- Pages: 3

## Geometry rules

- visible_area: positive-area intersection of MediaBox and CropBox
- coordinate_unit: raw PDF default user-space units
- physical_unit: pt = raw unit * UserUnit; mm = pt * 25.4 / 72
- displayed_dimensions: swap width/height for 90 or 270 degrees; unknown for non-90-degree rotation
- size_grouping: displayed width and height rounded to 0.001 pt; orientation-sensitive; unknown sizes excluded

## Document metadata

- /Producer: pypdf
- /Title: Three-page geometry sample

## Pages

| Page | MediaBox raw | CropBox raw | UserUnit | Rotate | Visible raw | Effective size before rotation | Displayed size | Orientation | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [0.0, 0.0, 595.276, 841.89] | [0.0, 0.0, 595.276, 841.89] | 1.0 | 0.0 | [0.0, 0.0, 595.276, 841.89] | 595.276 × 841.890 pt / 210.000 × 297.000 mm | 595.276 × 841.890 pt / 210.000 × 297.000 mm | portrait |  |
| 2 | [0.0, 0.0, 595.276, 841.89] | [0.0, 0.0, 595.276, 841.89] | 1.0 | 90.0 | [0.0, 0.0, 595.276, 841.89] | 595.276 × 841.890 pt / 210.000 × 297.000 mm | 841.890 × 595.276 pt / 297.000 × 210.000 mm | landscape |  |
| 3 | [0.0, 0.0, 612.0, 792.0] | [18.0, 36.0, 594.0, 756.0] | 1.0 | 0.0 | [18.0, 36.0, 594.0, 756.0] | 576.000 × 720.000 pt / 203.200 × 254.000 mm | 576.000 × 720.000 pt / 203.200 × 254.000 mm | portrait |  |

## Size groups

- 595.276 × 841.890 pt / 210.000 × 297.000 mm (portrait): pages 1
- 841.890 × 595.276 pt / 297.000 × 210.000 mm (landscape): pages 2
- 576.000 × 720.000 pt / 203.200 × 254.000 mm (portrait): pages 3
