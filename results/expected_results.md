# Expected results

## What I built

An auction agent that plays like a prudent investor: it skips auctions worth too little on
average, keeps savings at the bank up to the interest limit, bids the recent market price
per point plus a margin on the best auctions, and spends its savings over the last 100
rounds, before the final rush. Around it, an airbag checks every server message and every
bid, so a bad message skips a round instead of crashing the agent.

## Why a tournament

I do not know how strong the real class will be, and one game says little because of the
dice. So I measure my average place over many simulated games, against three plausible
classes of 20 players.

## How it works

The simulator plays a full 1000-round game in about 10 seconds without any server. It uses
the teacher's game engine (`AuctionHouse`) in the exact order of the real server, and my
agent answers with the exact code used in the real battle. The three classes:

- weak: my agent and 19 of the teacher's example agents
- mixed: my agent, 10 example agents and 9 copies of my agent with random settings
- strong: my agent and 19 copies of my agent with random settings

Every setting plays the same 20 games per class (same random seeds), so only my setting
changes between two rows. In total, about 1,300 games were played.

## How I chose the settings

1. One setting at a time, starting from my first version: 11 variants (`tournament.md`).
2. The best ideas combined: 4 combinations (`combinations.md`).
3. The best combination confirmed on 20 new games per class, never used before
   (`confirmation.md`).

The winner skips auctions worth less than 8 points on average (instead of 2), bids the
market price plus 30% (instead of 15%) and follows the market over the last 10 rounds
(instead of 20). Savings and endgame settings made almost no difference.

## Expected results

Average place out of 20 on the confirmation games (lower is better), then the grades:

| class  | first version         | final version             |
| ------ | --------------------- | ------------------------- |
| weak   | 1.0 (A 20)            | 1.0 (A 20)                |
| mixed  | 10.2 (C 4, D 15, E 1) | 8.6 (B 1, C 8, D 11)      |
| strong | 15.6 (D 2, E 18)      | 2.7 (A 16, B 1, C 2, D 1) |

I expect to finish between 1st and 9th, most likely around the middle of the top half:
grade C in a class like my mixed one, A or B in a class of serious agents, A against
weak agents.

## What makes it vary

- The class: by far the biggest factor. In the mixed class, the teacher's "tiny bid"
  agent, which bids a little on every auction, often wins, because it gets the small
  auctions that nobody else wants for almost nothing. A class with many such agents would
  push me down.
- Luck: within the same class, my place moves by a few ranks from game to game (see the
  grade spread above).
- Strategies close to mine: when many players bid the market price, they push prices up
  for each other.
- Game length: the settings were tuned for 1000 rounds.
- Crashes and network drops of other agents, which my simulator does not model.

My opponents are only the teacher's agents and copies of my own, so the real class may
behave differently.

Selling points for gold is not taken into account so far: my agent never sells points,
and no variant in the tournament tried it.

These results assume my default settings and no manual change during the game. I plan a
small control panel to adjust the main settings between or during games if the real class
behaves differently from my simulations.
