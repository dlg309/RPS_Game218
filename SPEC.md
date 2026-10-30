# Rock, Paper, Scissors

## RPS-001: Play a round

**Purpose:** one person plays a quick round against the computer.

- Choose rock, paper, or scissors. The computer chooses one move for that round.
- Display both choices and the result: **You win!**, **Computer wins**, or **It’s a tie**.
- Choosing again starts an independent round. No score; the requested temporary
  history below does not affect winner selection.
- Keep the supplied interface and server. Name/color changes can wait until the rules work.

### Expected results

Results are from the **player’s perspective**. `determine_winner(player, computer)` in `game.py` returns `win`, `lose`, or `tie`. Inputs are the lowercase moves below; the supplied server rejects other choices.

| Player | Computer | Expected return | Why the result makes sense |
| --- | --- | --- | --- |
| rock | rock | tie | Both chose rock. |
| rock | paper | lose | Paper beats rock. |
| rock | scissors | win | Rock beats scissors. |
| paper | rock | win | Paper beats rock. |
| paper | paper | tie | Both chose paper. |
| paper | scissors | lose | Scissors beat paper. |
| scissors | rock | lose | Rock beats scissors. |
| scissors | paper | win | Scissors beat paper. |
| scissors | scissors | tie | Both chose scissors. |

### Agreed plan

- Implement the nine player-perspective outcomes above in `determine_winner`.
  Keep the supplied Flask server and move controls; every choice decides a new,
  independent round. No scoring, accounts, new framework, or AI API.
- Prediction: the student predicted a loss when choosing rock against paper.
  The agent explained that paper beats rock. This is a valid losing round.
- Rejection: the student requested a helpful prompt for a valid move when an
  unsupported move is submitted. Reuse the supplied checks that missing input
  and unsupported input such as `lizard` return HTTP 400 with the allowed moves.
- Add nine explicit unit outcomes, real request/result integration tests, and a
  Chromium round/replay test using the supplied fixtures. Positive tests fix
  only the computer's random choice and use the real winner function.
- Run the full `.venv/bin/python check.py`, inspect all changed/new files against
  this plan, discuss one actual test, then have the student play and report a
  round and keyboard/replay observations before recording that evidence.

### Requested extension: latest three games

The student also requested a history showing the past three games. This extends
the assignment's original no-history scope; the one-round rules above stay
independent of previous results.

- Below the supplied game controls, show up to three completed rounds, newest
  first, including the player's move, computer's move, and result.
- Include the current round once it completes. After a fourth round, discard the
  oldest entry. Example: rounds A, B, C, D leave D, C, B.
- Store only those three entries in a signed browser-session cookie. There is
  no database or account. History is isolated by browser session and clears on
  server restart because the signing key is generated at startup. Browsers that
  restore session cookies may retain history until the server restarts.
- Opening the starting page or rejecting input must not add history entries.
  Show a friendly empty state before the first completed round.
- Check the three-entry limit and order, rejected-input behavior, and separation
  between clients with real requests. Verify displayed history and replay in
  Chromium, including discarding the oldest of four completed rounds.

### Checks

Agreed test coverage:

| Level | Cases and evidence |
| --- | --- |
| Unit — positive | All nine literal expected results above, including valid losses and ties. |
| Integration — positive | A submitted round uses the real rule function and displays both choices and the correct result. Fix the computer choice for the test. |
| Integration — negative | Reuse supplied missing/unsupported-move tests: HTTP 400 and a helpful explanation, without calling the rules. A crash is not the intended result. |
| E2E — positive | Add a real-browser round and replay in tests/e2e/test_round.py using the supplied live_server/page fixtures. Fix only the computer choice; use real rules and real HTTP. |

Use `unit`, `integration`, and `e2e` pytest markers. Run `.venv/bin/python check.py` for Black, Pylint, fast tests, and browser checks; then review the diff. Keep shared settings and meaningful assertions intact. The student still plays, inspects a rule and its test, and gives feedback. Browser automation does not establish every aspect of usability or application performance.

### Work record

- Issue: [RPS-001: Play a round — #1](https://github.com/dlg309/RPS_Game218/issues/1).
- Pull request / CI: add actual URLs when they exist.
- Implementation: [winner rules](game.py), [round requests and session history](app.py),
  [supplied interface with recent games](templates/index.html), and
  [history styling](static/style.css).
- Tests: [nine explicit outcomes and real request/history checks](tests/test_game.py)
  and [Chromium round, keyboard replay, and history limit](tests/e2e/test_round.py).
  Supplied missing/unsupported-input checks remain in
  [the unchanged shell tests](tests/test_shell.py).
- Original rules/history full local check (2026-10-30), Python 3.12.14:
  `.venv/bin/python check.py` exited 0. Black and Pylint passed; non-browser
  pytest: 28 passed (9 unit and 19 integration); Chromium: 7 passed. This covers
  the implemented rules and history as well as the original starter checks.
- Review: compared the changed files with the official starter and the agreed
  scope, and read both new test files. The supplied check runner, CI workflow,
  pinned requirements, tool settings, fixtures, and original test files are
  unchanged. New positive tests fix only randomness and call the real rules.
  History changes require `app.py`, the template, and CSS in addition to the
  four files originally expected for the rules-only assignment.
- Automated browser observation: rock against paper showed `Computer wins`;
  Tab selected Rock, the next Tab selected Paper, and Enter played paper
  against rock with `You win!`. Both rounds appeared in history. A separate
  four-round journey displayed only the newest three entries in the right order.
- Test discussion: the actual `test_rock_loses_to_paper` asserts that
  `determine_winner("rock", "paper") == "lose"`. At the student's request, the
  agent explained that this catches incorrect winner logic returning `win` or
  `tie` for rock against paper, because paper beats rock.
- Student browser review (2026-10-30): the student reported choosing scissors
  against the computer's scissors and seeing `It’s a tie`. They explained that
  the result is correct because both chose the same option. They also confirmed
  that Tab and Enter worked to play again and that the history showed the latest
  three games. The automated observations above describe the agent's checks.
- All-outcome review (2026-10-30): at the student's request, the agent verified
  all nine rows in the expected-results table, including the reasons now shown
  there. A Python verification script called the real winner function and made
  nine POST requests through Flask's test client, fixing only the computer's
  random choice. All nine returned HTTP 200 and displayed the expected result
  and both moves. After every round, the script checked that history matched
  the latest completed rounds in newest-first order, with at most three entries.
  All assertions passed. These are agent-run integration checks; the student's
  personally reported observation remains the scissors-versus-scissors tie.
- Help received: the coding agent imported the starter, explained the predicted
  matchup, saved the agreed plan and requested history extension, implemented
  the changes, explained the actual rock-versus-paper test and the mistake it
  catches, and ran/reviewed the checks.
- Starter setup (2026-10-30): imported all 20 files unchanged from official
  starter commit `3983604d8e83de8fc9aadf792150df87e2961047` into this existing
  repository. Python 3.12.14; full baseline check passed Black, Pylint, 13
  non-browser tests, and 5 Chromium tests. The student supplied a screenshot of
  the starting page with the unfinished-rules notice. This was baseline evidence
  only, not proof of completed winner rules.

## Requested extension: confetti and longest winning streak

- On a player win, play a short confetti animation. Do not celebrate a computer
  win, tie, rejected input, or a visit to the starting page. Replay must remain
  usable during the animation. Remove the confetti after it finishes.
- Respect the browser's reduced-motion preference: keep the result and streak
  visible while skipping the animation. Use local CSS/JavaScript with no new
  dependencies or external services.
- Show the player's longest winning streak and current streak in a panel on the
  right of the game on wide screens; stack the panel on narrow screens.
- Each win increases the current streak by one. At the student's explicit
  request, ties leave it unchanged. A loss resets only the current streak to
  zero. The longest streak is the largest current streak reached.
- Example sequence proposed by the agent: win, win, tie, loss leaves the current
  streak at zero and the longest streak at two. A subsequent win leaves current
  one and longest two. Four wins can produce a longest streak of four even
  though history stores only the last three games.
- Keep both counts with the existing temporary browser-session history. They
  start at zero, remain separate between clients, survive viewing the starting
  page, and reset when the server restarts. Rejected moves do not affect them.
- Validation: add real-request sequence checks and browser checks for winning
  confetti, cleanup, replay, ties, losses, the retained record, and reduced motion.
  Preserve the original winner rules and existing checks.

### Extension evidence (2026-10-30)

- Implementation: [session streak updates](app.py), [streak panel](templates/index.html),
  [local confetti script](static/confetti.js), and [responsive styling](static/style.css).
- Tests: [real-request streak sequences](tests/test_streaks.py) and
  [Chromium celebration and motion-preference checks](tests/e2e/test_celebration.py).
- Final full `.venv/bin/python check.py`, Python 3.12.14: exit 0, Black and
  Pylint passed, 38 non-browser tests passed, and 10 Chromium tests passed
  (48 total). The supplied check settings and original tests remain unchanged.
- Browser verification used real move submissions and fixed only the computer's
  random choice. Win, win, tie, loss, win produced the displayed current/best
  streaks 1/1, 2/2, 2/2, 0/2, 1/2. Confetti appeared only on wins, disappeared
  after its animation, and did not block replay. Reduced motion suppressed it
  while preserving the result and streak.
- Review found that a motion-preference change during the animation could leave
  hidden confetti elements. A direct media-query change listener now removes
  them; a new Chromium regression test confirms this behavior.
- Additional browser inspection verified that the panel sits to the right at
  1280 pixels and stacks below the game at 375 pixels, with no horizontal
  overflow. Real winning requests returned HTTP 200 and no browser JavaScript
  errors or failed network requests occurred. Screenshots were inspected locally.
- Remaining review finding: refreshing the completed POST can replay the form
  submission. The agent reproduced one move click followed by a browser reload
  sending two POSTs and increasing the current streak from 1 to 2. The supplied
  server's form-response pattern is retained; a redirect-after-submit flow is a
  recommended follow-up. Open the starting address with GET to avoid resubmission.
- The student's browser feedback above covers the earlier rules/history version.
  Student review and discussion of an actual new streak test remain to be recorded
  for this extension. These new automated observations are the agent's checks.
