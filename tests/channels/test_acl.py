import asyncio

import pytest


def test_allow_all_acl():
    from fast_channels.acl import AllowAllChannelACL

    acl = AllowAllChannelACL()
    assert asyncio.run(acl.may_subscribe("u", "c")) is True


def test_static_acl():
    from fast_channels.acl import StaticChannelACL

    acl = StaticChannelACL({"u1": {"a", "b"}})
    assert asyncio.run(acl.may_subscribe("u1", "a")) is True
    assert asyncio.run(acl.may_subscribe("u1", "z")) is False
    assert asyncio.run(acl.may_subscribe("u2", "a")) is False


def test_make_subscribe_acl_checker_raises():
    from fast_channels.acl import StaticChannelACL, make_subscribe_acl_checker
    from starlette.exceptions import WebSocketException

    acl = StaticChannelACL({"u1": {"ok"}})
    check = make_subscribe_acl_checker(acl, user_id="u1")

    async def run_ok():
        await check("ok")

    asyncio.run(run_ok())

    async def run_denied():
        await check("nope")

    with pytest.raises(WebSocketException) as ei:
        asyncio.run(run_denied())
    assert ei.value.code == 1008
