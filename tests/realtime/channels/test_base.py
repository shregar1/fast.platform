"""Tests for channels base (IChannelBackend interface)."""

import pytest

from realtime.channels.base import IChannelBackend
from tests.realtime.channels.abstraction import IChannelTests


class TestBase(IChannelTests):
    """Represents the TestBase class."""

    def test_channel_backend_abstract(self):
        """Execute test_channel_backend_abstract operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(TypeError):
            IChannelBackend()
