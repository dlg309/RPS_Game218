"""Real winner rules, submitted rounds, and the requested three-game history."""

import pytest

import app as web
from game import determine_winner


@pytest.mark.unit
def test_rock_ties_rock():
    """Equal rock moves tie."""
    assert determine_winner("rock", "rock") == "tie"


@pytest.mark.unit
def test_rock_loses_to_paper():
    """Paper beats the player's rock."""
    assert determine_winner("rock", "paper") == "lose"


@pytest.mark.unit
def test_rock_beats_scissors():
    """The player's rock beats scissors."""
    assert determine_winner("rock", "scissors") == "win"


@pytest.mark.unit
def test_paper_beats_rock():
    """The player's paper beats rock."""
    assert determine_winner("paper", "rock") == "win"


@pytest.mark.unit
def test_paper_ties_paper():
    """Equal paper moves tie."""
    assert determine_winner("paper", "paper") == "tie"


@pytest.mark.unit
def test_paper_loses_to_scissors():
    """Scissors beat the player's paper."""
    assert determine_winner("paper", "scissors") == "lose"


@pytest.mark.unit
def test_scissors_lose_to_rock():
    """Rock beats the player's scissors."""
    assert determine_winner("scissors", "rock") == "lose"


@pytest.mark.unit
def test_scissors_beat_paper():
    """The player's scissors beat paper."""
    assert determine_winner("scissors", "paper") == "win"


@pytest.mark.unit
def test_scissors_tie_scissors():
    """Equal scissors moves tie."""
    assert determine_winner("scissors", "scissors") == "tie"


@pytest.fixture(name="client")
def fixture_client():
    """Use an isolated browser-session cookie jar for each request test."""
    web.app.config.update(TESTING=True)
    return web.app.test_client()


@pytest.mark.integration
@pytest.mark.parametrize(
    ("player", "computer", "expected"),
    [
        ("rock", "paper", ("lose", "Computer wins")),
        ("paper", "rock", ("win", "You win!")),
        ("scissors", "scissors", ("tie", "It’s a tie")),
    ],
)
def test_submitted_round_uses_real_rules(
    client, monkeypatch, player, computer, expected
):
    """A real request shows both moves and the literal player-perspective result."""
    outcome, heading = expected
    monkeypatch.setattr(web.random, "choice", lambda _moves: computer)
    response = client.post("/", data={"move": player})
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert f'class="result" data-outcome="{outcome}"' in page
    assert f'<h2 id="game-heading">{heading}</h2>' in page
    assert "You chose" in page and "Computer chose" in page
    assert f'class="choice-value">{player.capitalize()}' in page
    assert f'class="choice-value">{computer.capitalize()}' in page
    assert "game rules not built yet" not in page


@pytest.mark.integration
def test_history_keeps_only_latest_three_completed_rounds(client, monkeypatch):
    """A fourth real round drops the oldest and keeps newest-first ordering."""
    computer_moves = iter(["paper", "rock", "scissors", "rock"])
    monkeypatch.setattr(web.random, "choice", lambda _moves: next(computer_moves))
    for player in ("rock", "paper", "scissors", "scissors"):
        response = client.post("/", data={"move": player})
        assert response.status_code == 200
    with client.session_transaction() as saved:
        assert saved["history"] == [
            {"player": "scissors", "computer": "rock", "outcome": "lose"},
            {"player": "scissors", "computer": "scissors", "outcome": "tie"},
            {"player": "paper", "computer": "rock", "outcome": "win"},
        ]
    page = response.get_data(as_text=True)
    assert page.count('class="history-round"') == 3
    assert 'data-history-player="rock" data-history-computer="paper"' not in page


@pytest.mark.integration
def test_starting_page_and_rejected_moves_preserve_history(client, monkeypatch):
    """GET and failed submissions never count as completed games."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "paper")
    initial = client.get("/")
    assert initial.status_code == 200
    assert b"Play a round to start your history." in initial.data
    assert client.post("/", data={"move": "rock"}).status_code == 200
    assert client.get("/").status_code == 200
    for data in ({}, {"move": "lizard"}):
        response = client.post("/", data=data)
        assert response.status_code == 400
        assert b"Choose Rock, Paper, or Scissors to play." in response.data
        assert response.data.count(b'class="history-round"') == 1
    with client.session_transaction() as saved:
        assert saved["history"] == [
            {"player": "rock", "computer": "paper", "outcome": "lose"}
        ]


@pytest.mark.integration
def test_history_is_separate_between_clients(client, monkeypatch):
    """Another browser session cannot see the first client's rounds."""
    monkeypatch.setattr(web.random, "choice", lambda _moves: "paper")
    assert client.post("/", data={"move": "rock"}).status_code == 200
    other_client = web.app.test_client()
    page = other_client.get("/").get_data(as_text=True)
    assert "Play a round to start your history." in page
    assert 'class="history-round"' not in page
    assert client.get("/").data.count(b'class="history-round"') == 1
