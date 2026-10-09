# Expected results

## Expected result

I expect a grade between B and D (place 4 to 12 out of 20). My simulations are more
optimistic, but my opponents there are only the teacher's agents and copies of my own.
Where I land depends mostly on how strong the real class is, on how many agents bid a
little on every auction, and on whether the bank keeps buying points back at more than
twice my market price, which is what makes selling pay.

## What I built

An auction agent that plays like a prudent investor:

- it skips auctions worth less than 8 points on average;
- it keeps savings at the bank up to the interest limit;
- it bids the recent market price per point plus 30% on the best auctions;
- when the bank buys points back at least twice as dear as the market price, it sells 2%
  of its points and spends the gold on new auctions (never in the last 110 rounds, never
  below 500 points);
- it spends its savings over the last 100 rounds, before the final rush.

## Why I expect this: simulations

A simulator plays a full 1000-round game in about 10 seconds with the teacher's game
engine, in the exact order of the real server, and with the exact code of my agent. I play
the same 20 games for every setting against three classes of 20 players:

- weak: 19 of the teacher's example agents
- mixed: 10 example agents and 9 copies of my agent with random settings
- strong: 19 copies of my agent with random settings

I changed one setting at a time, combined the best ones, added point selling, and
confirmed every choice on 20 new games per class. About 2,300 games in total. Average place
out of 20 on the confirmation games (lower is better), then the grades:

| class  | first version        | without selling           | final version        |
| ------ | -------------------- | ------------------------- | -------------------- |
| weak   | 1.0 (A 20)           | 1.0 (A 20)                | 1.0 (A 20)           |
| mixed  | 9.9 (C 4, D 15, E 1) | 8.6 (B 1, C 8, D 11)      | 6.9 (B 5, C 12, D 3) |
| strong | 15.6 (D 2, E 18)     | 2.7 (A 16, B 1, C 2, D 1) | 1.0 (A 20)           |

## Why I expect it to hold up on the day

A crash or a long disconnection loses rounds, and 10 points or less is an F, so I tested
the agent as much as its strategy :

- 10,000 random or broken server messages, with selling on and off: no crash, every
  answer valid, 99% of answers in under 0.5 ms.
- Two full local games of 1000 rounds against 19 of the teacher's agents, with no
  intervention: 1st of 20 both times.
- A 20-second network cut: the agent called back on its own and found the same account.
- A killed process, restarted over an encrypted connection like on the real server: the
  server took it back with its points.
- It never calls back after the end of a game, which would reset the scoreboard for
  everyone, and it asks before connecting to a finished game.

## What could change it

- The class: by far the biggest factor. The teacher's "tiny bid" agent, which bids a little
  on every auction, often wins the small auctions for almost nothing; a class with many
  such agents would push me down.
- The bank's rate for points: in my simulations the teacher's agents overpay and push it
  up, and nobody else sells cleverly. Against a more careful class the agent simply sells
  less.
- Luck: within the same class, my place moves by a few ranks from game to game.
- Strategies close to mine push prices up for each other.
- The settings are tuned for games of about 1000 rounds.

A small control panel (TUI) lets me adjust the margin and the minimum value, switch selling off
or pause the agent during a game if the real class behaves differently from my
simulations.
