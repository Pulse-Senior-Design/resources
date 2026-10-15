# Pulse design diagrams

The Canvas upload is [Assignment_4_Consolidated.pdf](Assignment_4_Consolidated.pdf). It contains User Stories, D0, D1, D2, and the peer-review notes in that order. Each team member submits the full PDF separately.

Assignment 4 names the complete design-diagram collection. D1 is the Assignment 6 work; D2 is the Assignment 7 update. D0 keeps its original header.

## Sources

- `D1_Detailed_Design.md`: the earlier Node and Hub design, edited for clarity.
- `D2_Detailed_Design.md`: completed component designs, error handling, traceability, and rationale.
- `Peer_Review_Notes.md`: feedback from Street Smart and EpistemicRAG, our responses, and the two issues we raised about Street Smart.
- `D1_Hub_Schema.sql`: the proposed database schema; not a migration.
- SVG/PNG files: editable diagrams and their Markdown images. The original D1 model is unchanged; `D1_Hub_Data_Model` adds the figure heading and legend.
- `../../../User_Stories.md`: the stories and acceptance criteria, including the clarified delivery deadline.

## Rebuild

Install Python packages `reportlab`, `pypdf`, `pypdfium2`, and `svglib`, then run:

```bash
python3 build_d2.py
```

This rebuilds User Stories at the repository root and the D1, D2, and consolidated PDFs in this folder. Review notes appear once, at the end of D2. Use this exporter for the current package; `build_d1.py` is the earlier D1-only exporter.

The original D0 files remain unchanged, including the copies under `../assignments/assignment-5/`.
