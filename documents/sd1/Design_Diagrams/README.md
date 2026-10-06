# Pulse design diagrams

The D1 submission file is `D1_Detailed_Design.pdf`.
The document includes all six assignment parts and all three team names.
It details the Node (C3) and Hub (C5).

## Files

| File | Purpose |
| --- | --- |
| `D1_Detailed_Design.md` | Edit the document text. |
| `D1_Data_Model.svg` | Edit the data model figure. |
| `D1_Data_Model.png` | Use the figure export in Markdown. |
| `D1_Hub_Schema.sql` | Read the proposed Hub schema. Do not apply it as a migration to an existing database. |
| `build_d1.py` | Export the figure and PDF from the sources. |
| `D0_*` | Compare the unchanged D0 baseline with D1. |

The original D0 files remain in `../assignments/assignment-5/`.
The copies here have the same bytes as those files.

## Export

Use Python 3 with `reportlab`, `pypdfium2`, and `Pillow`.
Run this command from this folder:

```bash
python3 build_d1.py
```

The script creates `D1_Detailed_Design.pdf` and `D1_Data_Model.png`.
It keeps the SVG figure as vector data inside the PDF.
The figure renderer supports the rectangles, lines, and text in the supplied SVG.

## Design status

D1 defines target behavior and marks changes from the current code.
The project code remains unchanged.
The design uses a 3,600-second expiry and 30-second retries.
Its reliable queue stays in memory until D2 defines persistent storage.
The document states planning sizes and the conflicting budget records.
It does not claim measured farm capacity or completed hardware tests.

## Submission

Submit the complete PDF separately for each team member.
Keep the PDF, text source, figure source, and export script in the team repository.
The course site submission remains a team action.
