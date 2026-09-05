# omega_vision

The **SoW Appendix A.2 package layout** for *Image Perception to Recognizable
Memory* (v1.9 — OmegaClaw / Hyperon–PLN).

This package lays out the **SoW-named classes** exactly as the Statement of Work
prescribes. The implementations live elsewhere — chiefly in
[`object_memory`](../object_memory) — and are re-exported here under the SoW names
and module layout. The only net-new code here is: compact implementations for
SoW-laid-out names with no prior home (`ContourFillForm`, `GridIndividuator`,
`RasterSegmenter`, the recall accelerators, `GridMetrics`/`RasterMetrics`),
importable §16 future stubs, and a factory method or two (`new_memory`,
`new_writer`, `build_store`, `process_observation`).

```python
import omega_vision as ov
from omega_vision.core import SingleWriter, ResidualGate, PredictionLedger
from omega_vision.forms import GenerativeForm, CellLogoForm, ContourFillForm
from omega_vision.adapters import GridAdapter, GridIndividuator, SpriteAdapter, RasterSegmenter
```

Layout (SoW Appendix A.2):

```
omega_vision/
  core/       schemas single_writer atom_store encounter_log residual_gate
              identity_merge prediction_ledger rule_induction evaluation
  forms/      base cell_logo contour_fill  (+ layered_stroke, part_graph_3d -> future §16)
  adapters/   grid/ sprite/                (+ anime_sketch/, robot3d/ -> future §16)
  accelerators/ vector_trace/ perceptual_hash/ faiss_index/  (+ sketchformer/ -> future §16)
  environments/  arc_grids arcade_synthetic physics_fixed_cam manipulation
  configs/    adapters.yaml
  docs/       PROGRAMMERS_GUIDE.md
```

**Full class-and-method reference:** [`docs/PROGRAMMERS_GUIDE.md`](docs/PROGRAMMERS_GUIDE.md)
maps every SoW section and Appendix-A name to its implementation. Tests:
[`tests/test_omega_vision.py`](../../tests/test_omega_vision.py).
