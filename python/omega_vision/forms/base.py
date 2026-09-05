"""SoW Appendix A.2 ``forms/base.py`` / A.3 — the ``GenerativeForm`` interface.

The stored unit is a generative program that, replayed, redraws the object
(SoW §5). This module only *lays out* the SoW-named surface; the implementation
lives elsewhere in :mod:`object_memory.forms`.

SoW A.3 lists seven form methods: ``canonicalize``, ``render``, ``fit_instance``,
``residual``, ``code_length``, ``distance``, ``complete``. The primary
implementation (:class:`object_memory.forms.GenerativeForm`) provides
``canonicalize`` / ``render`` / ``fit_instance`` / ``distance``; the remaining
three are provided per-form (see :class:`omega_vision.forms.contour_fill.ContourFillForm`
and :meth:`object_memory.forms.CellLogoForm.description_length`) and, for the
``residual`` disposition, by :class:`object_memory.recognition.ResidualAnalyzer`
and :class:`object_memory.memory.ResidualGate`.
"""

from object_memory.forms import FitResult, GenerativeForm

__all__ = ["GenerativeForm", "FitResult"]
