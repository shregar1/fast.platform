"""Tests for channels base (IChannelBackend interface)."""
from tests.realtime.channels.abstraction import IChannelTests


import pytest

from channels.base import IChannelBackend


class TestBase(IChannelTests):

    def test_channel_backend_abstract(self):
        with pytest.raises(TypeError):
            IChannelBackend()
