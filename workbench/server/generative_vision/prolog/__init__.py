"""generative_vision.prolog — turn a rendered frame into a symbolic part-graph
without an LLM: perception (quantize / connected-components / topology) in
Python, grouping in SWI-Prolog.

Public entry point: ``symbolic_arc.extract_frame(png_path, char)``.

Runtime dependencies (to declare when this becomes a pip package):
  - Python: numpy, scipy, Pillow
  - System: SWI-Prolog (``swipl`` on PATH)
  - Package data: the ``*.pl`` rule files in this directory
"""
