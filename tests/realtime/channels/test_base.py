"""Tests for channels base (IChannelBackend interface)."""

import pytest

from realtime.channels.base import IChannelBackend
from tests.realtime.channels.abstraction import IChannelTests


class TestBase(IChannelTests):
    def test_channel_backend_abstract(self):
        with pytest.raises(TypeError):
            IChannelBackend()
