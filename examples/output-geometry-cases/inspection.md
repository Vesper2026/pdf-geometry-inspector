# PDF geometry inspection

- Input: D:\\workdata\\webprojects\\seo\\accounts\\Vesper2026\\pdf-geometry-inspector\\examples\\geometry_cases.pdf
- SHA-256: e20bcd3590fafb27919dfd94386fe6f5a36fd9dea536d35dd980d8b8f38d003a
- Status: ok
- PDF header: %PDF-1.7
- Encrypted: false
- Access: readable
- Pages: 10

## Geometry rules

- visible_area: positive-area intersection of MediaBox and CropBox
- coordinate_unit: raw PDF default user-space units
- physical_unit: pt = raw unit * UserUnit; mm = pt * 25.4 / 72
- displayed_dimensions: swap width/height for 90 or 270 degrees; unknown for non-90-degree rotation
- size_grouping: displayed width and height rounded to 0.001 pt; orientation-sensitive; unknown sizes excluded

## Document metadata

- /Producer: pypdf
- /Title: Synthetic PDF geometry cases
- /Author: PDF Geometry Inspector examples

## Pages

| Page | MediaBox raw | CropBox raw | UserUnit | Rotate | Visible raw | Effective size before rotation | Displayed size | Orientation | Warnings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [0.0, 0.0, 595.275591, 841.889764] | [0.0, 0.0, 595.275591, 841.889764] | 1.0 | 0.0 | [0.0, 0.0, 595.275591, 841.889764] | 595.276 × 841.890 pt / 210.000 × 297.000 mm | 595.276 × 841.890 pt / 210.000 × 297.000 mm | portrait |  |
| 2 | [0.0, 0.0, 595.275591, 841.889764] | [0.0, 0.0, 595.275591, 841.889764] | 1.0 | 90.0 | [0.0, 0.0, 595.275591, 841.889764] | 595.276 × 841.890 pt / 210.000 × 297.000 mm | 841.890 × 595.276 pt / 297.000 × 210.000 mm | landscape |  |
| 3 | [0.0, 0.0, 612.0, 792.0] | [54.0, 36.0, 558.0, 756.0] | 1.0 | 0.0 | [54.0, 36.0, 558.0, 756.0] | 504.000 × 720.000 pt / 177.800 × 254.000 mm | 504.000 × 720.000 pt / 177.800 × 254.000 mm | portrait |  |
| 4 | [0.0, 0.0, 200.0, 300.0] | [0.0, 0.0, 200.0, 300.0] | 2.0 | 0.0 | [0.0, 0.0, 200.0, 300.0] | 400.000 × 600.000 pt / 141.111 × 211.667 mm | 400.000 × 600.000 pt / 141.111 × 211.667 mm | portrait |  |
| 5 | [0.0, 0.0, 612.0, 792.0] | [-20.0, -10.0, 700.0, 900.0] | 1.0 | 0.0 | [0.0, 0.0, 612.0, 792.0] | 612.000 × 792.000 pt / 215.900 × 279.400 mm | 612.000 × 792.000 pt / 215.900 × 279.400 mm | portrait | crop_outside_media: CropBox extends outside MediaBox; visible geometry uses their intersection. |
| 6 | [0.0, 0.0, 612.0, 792.0] | [700.0, 800.0, 900.0, 1000.0] | 1.0 | 0.0 | None | unknown | unknown | unknown | crop_outside_media: CropBox extends outside MediaBox; visible geometry uses their intersection.; empty_intersection: MediaBox and CropBox have no positive-area intersection. |
| 7 | [0.0, 0.0, 612.0, 792.0] | [0.0, 0.0, 612.0, 792.0] | 1.0 | 45.0 | [0.0, 0.0, 612.0, 792.0] | 612.000 × 792.000 pt / 215.900 × 279.400 mm | unknown | unknown | non_90_rotation: Rotate is not a finite multiple of 90; displayed dimensions and orientation are unknown. |
| 8 | [0.0, 0.0, 612.0, 792.0] | [100.0, 0.0, 100.0, 792.0] | 1.0 | 0.0 | None | unknown | unknown | unknown | non_positive_cropbox: /CropBox has non-positive width or height; coordinates are not reordered. |
| 9 | [612.0, 0.0, 0.0, 792.0] | None | 1.0 | 0.0 | None | unknown | unknown | unknown | non_positive_mediabox: /MediaBox has non-positive width or height; coordinates are not reordered.; missing_cropbox: /CropBox is missing and has no usable default. |
| 10 | [0.0, 0.0, 595.275591, 841.889764] | [0.0, 0.0, 595.275591, 841.889764] | 1.0 | 270.0 | [0.0, 0.0, 595.275591, 841.889764] | 595.276 × 841.890 pt / 210.000 × 297.000 mm | 841.890 × 595.276 pt / 297.000 × 210.000 mm | landscape |  |

## Size groups

- 595.276 × 841.890 pt / 210.000 × 297.000 mm (portrait): pages 1
- 841.890 × 595.276 pt / 297.000 × 210.000 mm (landscape): pages 2, 10
- 504.000 × 720.000 pt / 177.800 × 254.000 mm (portrait): pages 3
- 400.000 × 600.000 pt / 141.111 × 211.667 mm (portrait): pages 4
- 612.000 × 792.000 pt / 215.900 × 279.400 mm (portrait): pages 5
- Unknown size, excluded: [6, 7, 8, 9]
