"""Real request checks for win celebrations and session winning streaks."""

import pytest

import app as web

pytestmark = pytest.mark.integration


@pytest.fixture(name="client")
def fixture_client():
    """Give each check its own browser-session cookie jar."""
    web.app.config.update(TESTING=True)
    return web.app.test_client()


@pytest.mark.parametrize(
    ("moves", "expected"),
    [
        (("rock", "rock", "rock", "rock"), (4, 4)),
        (("rock", "scissors", "rock"), (2, 2)),
        (("rock", "rock", "paper", "rock"), (1, 2)),
        (("scissors",), (0, 0)),
        (("paper",), (0, 0)),
    ],
)
def test_winning_streak_sequences(client, monkeypatch, moves, expected):
    """Wins add, ties preserve, and losses reset only the current streak."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    for move in moves:
        response = client.post("/", data={"move": move})
        assert response.status_code == 200
    current, best = expected
    with client.session_transaction() as saved:
        assert saved.get("current_streak", 0) == current
        assert saved.get("best_streak", 0) == best
        assert len(saved["history"]) == min(len(moves), 3)
    page = response.get_data(as_text=True)
    assert f'<dd id="current-streak">{current}</dd>' in page
    assert f'<dd id="best-streak">{best}</dd>' in page


def test_get_and_rejected_moves_do_not_change_streak(client, monkeypatch):
    """Viewing the page or rejecting a move cannot extend or break a streak."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    for _ in range(2):
        assert client.post("/", data={"move": "rock"}).status_code == 200
    assert client.get("/").status_code == 200
    for data in ({}, {"move": "lizard"}, {"move": ""}):
        assert client.post("/", data=data).status_code == 400
    with client.session_transaction() as saved:
        assert saved["current_streak"] == 2
        assert saved["best_streak"] == 2
        assert len(saved["history"]) == 2


def test_streak_is_separate_between_clients(client, monkeypatch):
    """One browser's record never becomes another browser's starting record."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    assert client.post("/", data={"move": "rock"}).status_code == 200
    other = web.app.test_client()
    page = other.get("/").get_data(as_text=True)
    assert '<dd id="current-streak">0</dd>' in page
    assert '<dd id="best-streak">0</dd>' in page
    with client.session_transaction() as saved:
        assert saved["current_streak"] == saved["best_streak"] == 1


@pytest.mark.parametrize(
    ("move", "celebrates"), [("rock", True), ("paper", False), ("scissors", False)]
)
def test_only_player_wins_include_confetti(client, monkeypatch, move, celebrates):
    """A loss, tie, or starting page cannot trigger a win celebration."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "scissors")
    response = client.post("/", data={"move": move})
    assert response.status_code == 200
    assert (b"/static/confetti.js" in response.data) is celebrates
    assert b"/static/confetti.js" not in client.get("/").data
