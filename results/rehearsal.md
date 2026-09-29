# Rehearsal and chaos tests

29 September 2026, on my laptop, with the teacher's server (dnd_auction_game 0.6.0) running
locally, the teacher's example agents as opponents, and my agent with its default settings
(empty `logs/control.json`).

## Results

| Test | How | Result |
|------|-----|--------|
| Full rehearsal | `make rehearsal ROUNDS=1000 OPPONENTS=19`, monitor open, no intervention | passed: 1st of 20 (A) |
| Network cut | a relay between my agent and the server, cut for 20 seconds at round 100 of 300 | passed: back with the same identity, 2nd of 6 (B) |
| End of the game | let the game finish | passed: the agent stopped by itself, no call back |
| Relaunch after the end | start the agent again once the game is over, answer `n` | passed: it asked first, the scoreboard stayed untouched |
| Killed process | `kill -9` at round 30, then start the agent again | partly: no crash, but refused locally (see limits) |

## Full rehearsal in numbers

- 1000 rounds, 1000 logbook lines, no unreadable round, never paused
- 48,603 points, 60% more than the 2nd (a "tiny bid" agent with 30,393)
- 1,662 bids won and 598 lost (73% win rate)
- response time: median 0.57 ms, 99% under 1.23 ms, slowest 1.88 ms (my target is under 10 ms, a round lasts about 1 second)

## Network cut in detail

The agent lost the line at round 100, tried again every 2 seconds while the relay was down,
and came back at round 120. The server logged `Agent Dylan reconnected`: same account, gold
and points kept. It missed 20 rounds and then played normally until the end.

## Limits

- On `localhost`, the teacher's client draws a new random identity at each start
  (`client.py`, lines 39 to 44), so an agent started again after `kill -9` counts as a new
  player and is refused in the middle of a game. On the real server the identity comes from
  the machine, so the same restart is a reconnection, which the network cut test shows the
  server accepts. This will be checked on the teacher's test server.
- The opponents are the teacher's example agents, not the real class.
- Trapped messages from the server are covered by the crash test (10,000 random or broken
  messages), not by these games.

## Second full rehearsal, with point selling

29 September 2026, same setup, with the final agent (selling 2% of its points when the bank
pays at least twice its market price), no intervention:

- 1st of 20 (A) with 43,586 points, almost three times the 2nd (14,962); points are not
  comparable between the two rehearsals, as each game draws its own dice, salaries and rates
- 1000 rounds, 1000 logbook lines, no unreadable round, never paused, no error
- 8,616 bids won and 2,411 lost (78% win rate)
- 274 sales, 123,108 points sold in total and bought back at auction with the gold; the last
  sale came 112 rounds before the end, as the rule forbids selling in the last 110 rounds
- response time: median 0.43 ms, 99% under 0.69 ms, slowest 0.87 ms
