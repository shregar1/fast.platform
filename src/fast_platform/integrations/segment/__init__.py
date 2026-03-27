"""
Segment Integration

Customer data platform.
"""

from .client import SegmentClient, track, identify, group, page

__all__ = [
    "SegmentClient",
    "track",
    "identify",
    "group",
    "page",
]
