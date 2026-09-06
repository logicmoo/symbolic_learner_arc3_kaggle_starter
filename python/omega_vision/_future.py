"""Shared scaffolding for SoW §16 "future" components.

The SoW lays these names out as *stubs only* (Appendix A.2 comments, A.8 task 9):
they must be importable so later models plug into an existing typed name, but they
carry no acceptance bar and are not implemented in this contract. Instantiating or
calling one raises :class:`FutureComponentError` with the SoW pointer.
"""

from __future__ import annotations


class FutureComponentError(NotImplementedError):
    """Raised when a SoW §16 future component is used before it is built."""


def future_component(name: str, section: str, note: str):
    """Build an importable stub class for a not-yet-in-scope SoW component."""

    class _Future:
        __doc__ = f"SoW {section} future component (stub only): {note}"
        component_name = name
        sow_section = section

        def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ANN002, ANN003
            raise FutureComponentError(
                f"{name} is a SoW {section} future component (stub only): {note}"
            )

    _Future.__name__ = name
    _Future.__qualname__ = name
    return _Future


__all__ = ["FutureComponentError", "future_component"]
