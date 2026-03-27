"""Base types for :mod:`utils`.

Concrete helpers in this package inherit :class:`IUtility` so call sites and
documentation can treat them as a consistent “utility” family, even though most
implementations use only static methods and carry no instance state.

Subpackages define narrower markers (e.g. :class:`~core.utils.media.abstraction.IMedia`,
:class:`~core.utils.clock.abstraction.IClockUtility`,
:class:`~core.utils.decimal.abstraction.IDecimalUtility`,
:class:`~core.utils.archive.abstraction.IArchiveUtility`) that inherit :class:`IUtility`;
prefer those for code under each subfolder.
"""

from __future__ import annotations

from abc import ABC


class IUtility(ABC):
    """Marker abstract base for utility classes under :mod:`utils`.

    Subclasses are typically collections of :func:`staticmethod` helpers (no shared
    mutable state). Inheriting from :class:`IUtility` documents intent and keeps
    typing / discovery consistent; it does not enforce a particular method set.
    """

    pass


__all__ = ["IUtility"]
