"""Tests for :mod:`realtime.channels.acl`."""

import asyncio

import pytest

from tests.realtime.channels.abstraction import IChannelTests


class TestAcl(IChannelTests):
    """Represents the TestAcl class."""

    def test_allow_all_acl(self):
        """Execute test_allow_all_acl operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.acl import AllowAllChannelACL

        acl = AllowAllChannelACL()
        assert asyncio.run(acl.may_subscribe("u", "c")) is True

    def test_static_acl(self):
        """Execute test_static_acl operation.

        Returns:
            The result of the operation.
        """
        from realtime.channels.acl import StaticChannelACL

        acl = StaticChannelACL({"u1": {"a", "b"}})
        assert asyncio.run(acl.may_subscribe("u1", "a")) is True
        assert asyncio.run(acl.may_subscribe("u1", "z")) is False
        assert asyncio.run(acl.may_subscribe("u2", "a")) is False

    def test_make_subscribe_acl_checker_raises(self):
        """Execute test_make_subscribe_acl_checker_raises operation.

        Returns:
            The result of the operation.
        """
        from starlette.exceptions import WebSocketException

        from realtime.channels.acl import StaticChannelACL, make_subscribe_acl_checker

        acl = StaticChannelACL({"u1": {"ok"}})
        check = make_subscribe_acl_checker(acl, user_id="u1")

        async def run_ok():
            """Execute run_ok operation.

            Returns:
                The result of the operation.
            """
            await check("ok")

        asyncio.run(run_ok())

        async def run_denied():
            """Execute run_denied operation.

            Returns:
                The result of the operation.
            """
            await check("nope")

        with pytest.raises(WebSocketException) as ei:
            asyncio.run(run_denied())
        assert ei.value.code == 1008
