"""Tests for channels base (ChannelBackend interface)."""

import pytest
from channels.base import ChannelBackend


def test_channel_backend_abstract():
    with pytest.raises(TypeError):
        ChannelBackend()  # type: ignore
