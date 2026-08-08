({}
  (kind prompt)
  (id turtle_motion_dsl)
  (label "Turtle Motion DSL Contract")
  (description "Exact movement-oriented Turtle vocabulary retained from the ARC3 work but shared because it is a general visual reconstruction representation.")
  (text (
    "Use the canonical motion vocabulary penup, pendown, set_pos/2, setcolor/1, pen_width/1, fwd/1, rot/1, and set_cell."
    "pen_width/1 accepts widths 1 through 4 logical cells. Use set_pos/2 to establish an initial position or begin a genuinely disconnected stroke; once positioned, trace geometry with fwd/1 and rot/1."
    "Prefer the largest exact pen width up to 4 when it paints exactly the intended cells."
    "Do not substitute rect/4, rectangle/4, fill/1, block/4, draw_cells/1, direct four-coordinate box commands, or long lists of independent cell placements when a motion program is required."
    "Preserve holes and disconnected geometry by tracing or scan-line motion rather than painting oversized blocks."
  ))
  (metadata ({}
    (domain vision)
    (representation turtle-dsl)
  ))
)
