"""Real browser checks for confetti, its cleanup, and the visible streak record."""

import pytest
from playwright.sync_api import Page, expect

import app as web

pytestmark = pytest.mark.e2e


def test_win_confetti_and_streak_replay(page: Page, live_server, monkeypatch):
    """Celebrate real wins, retain the record through ties/losses, and replay."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    page.goto(live_server)
    expect(page.locator("#current-streak")).to_have_text("0")
    expect(page.locator("#best-streak")).to_have_text("0")
    expect(page.locator(".confetti")).to_have_count(0)

    page.get_by_role("button", name="Rock", exact=True).click()
    expect(page.locator(".result")).to_have_attribute("data-outcome", "win")
    expect(page.locator("#current-streak")).to_have_text("1")
    expect(page.locator("#best-streak")).to_have_text("1")
    expect(page.locator(".confetti")).to_be_visible()
    expect(page.locator(".confetti")).to_have_attribute("aria-hidden", "true")
    expect(page.locator(".confetti")).to_have_css("pointer-events", "none")
    expect(page.locator(".confetti-piece")).to_have_count(48)
    expect(page.locator(".confetti-piece").first).to_have_css(
        "animation-name", "confetti-fall"
    )
    expect(page.locator(".confetti")).to_have_count(0, timeout=5000)

    page.get_by_role("button", name="Rock", exact=True).click()
    expect(page.locator("#current-streak")).to_have_text("2")
    expect(page.locator("#best-streak")).to_have_text("2")
    expect(page.locator(".confetti")).to_be_visible()

    # Replay remains clickable while the celebration is on screen.
    page.get_by_role("button", name="Scissors", exact=True).click()
    expect(page.locator(".result")).to_have_attribute("data-outcome", "tie")
    expect(page.locator("#current-streak")).to_have_text("2")
    expect(page.locator("#best-streak")).to_have_text("2")
    expect(page.locator(".confetti")).to_have_count(0)

    page.get_by_role("button", name="Paper", exact=True).click()
    expect(page.locator(".result")).to_have_attribute("data-outcome", "lose")
    expect(page.locator("#current-streak")).to_have_text("0")
    expect(page.locator("#best-streak")).to_have_text("2")
    expect(page.locator(".confetti")).to_have_count(0)

    page.goto(live_server)
    expect(page.locator("#best-streak")).to_have_text("2")
    expect(page.locator(".confetti")).to_have_count(0)
    page.get_by_role("button", name="Rock", exact=True).click()
    expect(page.locator("#current-streak")).to_have_text("1")
    expect(page.locator("#best-streak")).to_have_text("2")
    expect(page.locator(".confetti")).to_be_visible()


def test_reduced_motion_keeps_win_without_confetti(
    page: Page, live_server, monkeypatch
):
    """Reduced-motion users still get the winning result and recorded streak."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    page.emulate_media(reduced_motion="reduce")
    page.goto(live_server)
    page.get_by_role("button", name="Rock", exact=True).click()
    page.wait_for_load_state("load")
    expect(page.get_by_role("heading", name="You win!", exact=True)).to_be_visible()
    expect(page.locator("#current-streak")).to_have_text("1")
    expect(page.locator("#best-streak")).to_have_text("1")
    expect(page.locator(".confetti")).to_have_count(0)


def test_enabling_reduced_motion_cleans_up_active_confetti(
    page: Page, live_server, monkeypatch
):
    """Changing motion preferences during the animation removes its overlay."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    page.goto(live_server)
    page.get_by_role("button", name="Rock", exact=True).click()
    expect(page.locator(".confetti")).to_be_visible()
    page.emulate_media(reduced_motion="reduce")
    expect(page.locator(".confetti")).to_have_count(0)
    expect(page.locator("#best-streak")).to_have_text("1")
