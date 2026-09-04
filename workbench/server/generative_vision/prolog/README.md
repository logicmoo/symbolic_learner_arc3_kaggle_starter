# generative_vision / prolog

LLM-free recognizers that produce the **same** part-graph the vision model does
(parts + partOf groups), for direct side-by-side comparison in the reduce
pipeline. **No bounding boxes** are used for grouping — only pixel topology
(`adjacent`, `encloses`); bbox is allowed only as a scale transform to grow or
shrink a subpart.

## Files

| file | role |
|------|------|
| `symbolic_arc.py` | Pipeline entry: PNG → exact grid → topology facts → **swipl** grouping → `metta` + `parts.json` (same schema as the LLM line). |
| `arc_group.pl` | bbox-free grouping the pipeline runs (`encloses`/`adjacent`, background suppression, object clusters). |
| `arc_parts.pl` | Standalone ARC flood-fill over `cell/3` grid facts. |
| `group_regions.pl` | Grouping for complex images (cartoon/CGI) over `region/4`+`adjacent/2`+`encloses/2`. |
| `pixels_to_grid.py` | Decode a flat-color ARC render back to its exact color grid (auto cell-pitch). |
| `pixels_to_regions.py` | Quantize + connected-components for complex images (cartoon/CGI); optional `--grid` cell/3. |

## Dependencies

- Python: `numpy`, `scipy`, `Pillow`
- System: **SWI-Prolog** (`swipl` on PATH)

## Packaging (TODO)

To ship as an installable package: add a `pyproject.toml` declaring the deps
above, include the `*.pl` files as `package_data`, and replace the current
`sys.path`-insert import in `video_import_pipeline.py` with
`from generative_vision.prolog import symbolic_arc`. `__init__.py` files are
already in place so the tree is import-ready.
