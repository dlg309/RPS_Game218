"""Real Chromium rounds, keyboard replay, and three-game history with real rules."""

import pytest
from playwright.sync_api import Page, expect

import app as web

pytestmark = pytest.mark.e2e


def test_round_and_keyboard_replay(page: Page, live_server, monkeypatch):
    """Play a real losing round, then use the keyboard to play a winning round."""
    computer_moves = iter(["paper", "rock"])
    monkeypatch.setattr(web.random, "choice", lambda _moves: next(computer_moves))
    page.goto(live_server)
    expect(page.get_by_text("Play a round to start your history.")).to_be_visible()
    expect(page.get_by_role("status")).to_have_count(0)

    page.get_by_role("button", name="Rock", exact=True).click()
    choices = page.get_by_label("This round’s choices")
    expect(choices.locator(".choice-value")).to_have_text(["Rock ✊", "Paper ✋"])
    expect(
        page.get_by_role("heading", name="Computer wins", exact=True)
    ).to_be_visible()
    expect(page.locator(".result")).to_have_attribute("data-outcome", "lose")

    # The first focusable control is Rock; Tab advances to Paper and Enter submits.
    page.keyboard.press("Tab")
    expect(page.get_by_role("button", name="Rock", exact=True)).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.get_by_role("button", name="Paper", exact=True)).to_be_focused()
    page.keyboard.press("Enter")
    expect(choices.locator(".choice-value")).to_have_text(["Paper ✋", "Rock ✊"])
    expect(page.get_by_role("heading", name="You win!", exact=True)).to_be_visible()
    expect(page.locator(".result")).to_have_attribute("data-outcome", "win")
    expect(page.locator(".history-round")).to_have_text(
        [
            "You: Paper · Computer: Rock You win!",
            "You: Rock · Computer: Paper Computer wins",
        ]
    )


def test_history_discards_oldest_after_four_rounds(
    page: Page, live_server, monkeypatch
):
    """The browser displays exactly the newest three completed rounds in order."""
    computer_moves = iter(["paper", "rock", "scissors", "rock"])
    monkeypatch.setattr(web.random, "choice", lambda _moves: next(computer_moves))
    page.goto(live_server)
    for move, outcome in (
        ("Rock", "lose"),
        ("Paper", "win"),
        ("Scissors", "tie"),
        ("Scissors", "lose"),
    ):
        page.get_by_role("button", name=move, exact=True).click()
        expect(page.locator(".result")).to_have_attribute("data-outcome", outcome)

    history = page.get_by_role("region", name="Recent games")
    expect(history.locator(".history-round")).to_have_text(
        [
            "You: Scissors · Computer: Rock Computer wins",
            "You: Scissors · Computer: Scissors It’s a tie",
            "You: Paper · Computer: Rock You win!",
        ]
    )
    # Return to GET rather than refreshing a POST, so no round is resubmitted.
    page.goto(live_server)
    expect(
        page.get_by_role("heading", name="Your next move?", exact=True)
    ).to_be_visible()
    expect(history.locator(".history-round")).to_have_count(3)
    expect(history.locator(".history-round").first).to_contain_text(
        "You: Scissors · Computer: Rock"
    )
