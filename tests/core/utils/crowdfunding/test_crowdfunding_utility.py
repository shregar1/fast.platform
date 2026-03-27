"""Tests for :class:`~core.utils.crowdfunding.CrowdfundingUtility`."""

from __future__ import annotations

from fast_platform.core.utils.crowdfunding import CrowdfundingUtility


def test_percent_funded_basic():
    """Execute test_percent_funded_basic operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.percent_funded(50_00, 100_00) == 50.0


def test_percent_funded_over_goal():
    """Execute test_percent_funded_over_goal operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.percent_funded(150_00, 100_00) == 150.0


def test_percent_funded_zero_goal():
    """Execute test_percent_funded_zero_goal operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.percent_funded(10, 0) == 0.0


def test_remaining_goal_cents():
    """Execute test_remaining_goal_cents operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.remaining_goal_cents(30_00, 100_00) == 70_00
    assert CrowdfundingUtility.remaining_goal_cents(100_00, 100_00) == 0


def test_is_goal_met():
    """Execute test_is_goal_met operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.is_goal_met(100_00, 100_00) is True
    assert CrowdfundingUtility.is_goal_met(99_99, 100_00) is False
    assert CrowdfundingUtility.is_goal_met(100_00, 0) is False


def test_normalize_campaign_slug():
    """Execute test_normalize_campaign_slug operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.normalize_campaign_slug("  My Cool Project!  ") == "my-cool-project"
    assert CrowdfundingUtility.normalize_campaign_slug("") == "project"


def test_pledge_covers_reward():
    """Execute test_pledge_covers_reward operation.

    Returns:
        The result of the operation.
    """
    assert CrowdfundingUtility.pledge_covers_reward(25_00, 25_00) is True
    assert CrowdfundingUtility.pledge_covers_reward(30_00, 25_00) is True
    assert CrowdfundingUtility.pledge_covers_reward(24_00, 25_00) is False
