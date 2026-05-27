from __future__ import annotations

from enum import IntEnum

from PyQt6.QtCore import Qt


class _FallbackColorScheme(IntEnum):
    Unknown = 0
    Dark = 1
    Light = 2


QtColorScheme = getattr(Qt, "ColorScheme", _FallbackColorScheme)

