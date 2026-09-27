"""Plays one simulated game and prints the ranking (think: one flight in the simulator)"""

import argparse
import time

from smaug.sim.classes import CLASSES, OUR_NAME
from smaug.sim.engine import play_game
from smaug.sim.grades import grade_for


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="make sim")
    parser.add_argument("--class", dest="class_name", choices=list(CLASSES), default="mixed")
    parser.add_argument("--rounds", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=1)
    values = parser.parse_args(arguments)

    start = time.perf_counter()
    ranking = play_game(CLASSES[values.class_name], values.rounds, values.seed)
    seconds = time.perf_counter() - start

    print(f"{values.class_name} class, {values.rounds} rounds, seed {values.seed}, {seconds:.1f} s")
    print()
    print("place  grade   points     gold  name")
    for place_index, (points, gold, name) in enumerate(ranking):
        grade = grade_for(place_index, len(ranking), points)
        marker = "   <- us" if name == OUR_NAME else ""
        print(f"{place_index + 1:>5}  {grade:>5}  {points:>7}  {gold:>7}  {name}{marker}")


if __name__ == "__main__":
    main()
