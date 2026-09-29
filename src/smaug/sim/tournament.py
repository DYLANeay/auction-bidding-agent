"""Many simulated games per class and per setting, on all CPU cores (think: the training championship)"""

import argparse
import os
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path
from statistics import mean

from smaug.agent.config import DEFAULT_SETTINGS, NO_SELLING_SETTINGS, V1_SETTINGS
from smaug.sim.classes import CLASSES, OUR_NAME
from smaug.sim.engine import play_game
from smaug.sim.grades import grade_for
from smaug.sim.players import Player

# "current" suit les réglages par défaut ; les autres variantes partent de la première version (v1)
VARIANTS = {
    "current": DEFAULT_SETTINGS,
    "no selling": NO_SELLING_SETTINGS,
    "v1": V1_SETTINGS,
    # étape 2 : un seul réglage change par rapport à la v1
    "min EV 4": replace(V1_SETTINGS, min_expected_value=4),
    "min EV 6": replace(V1_SETTINGS, min_expected_value=6),
    "min EV 8": replace(V1_SETTINGS, min_expected_value=8),
    "savings 50%": replace(V1_SETTINGS, reserve_factor=0.5),
    "savings 140%": replace(V1_SETTINGS, reserve_factor=1.4),
    "margin 5%": replace(V1_SETTINGS, margin=0.05),
    "margin 30%": replace(V1_SETTINGS, margin=0.30),
    "window 10": replace(V1_SETTINGS, history_rounds=10),
    "window 40": replace(V1_SETTINGS, history_rounds=40),
    "endgame margin 30%": replace(V1_SETTINGS, endgame_margin=0.30),
    "endgame margin 100%": replace(V1_SETTINGS, endgame_margin=1.00),
    # étape 3 : les meilleures idées combinées (combo C est devenu les réglages par défaut)
    "combo A": replace(V1_SETTINGS, min_expected_value=8, margin=0.30),
    "combo B": replace(V1_SETTINGS, min_expected_value=6, margin=0.30),
    "combo C": replace(V1_SETTINGS, min_expected_value=8, margin=0.30, history_rounds=10),
    "combo D": replace(V1_SETTINGS, min_expected_value=6, margin=0.30, history_rounds=10),
    # vente de points : les réglages de la bataille, plus la vente (sous-issue #33)
    "sell 0.5% x2": replace(DEFAULT_SETTINGS, sell_share=0.005, sell_ratio=2.0),
    "sell 1% x2": replace(DEFAULT_SETTINGS, sell_share=0.01, sell_ratio=2.0),
    "sell 2% x2": replace(DEFAULT_SETTINGS, sell_share=0.02, sell_ratio=2.0),
    "sell 3% x2": replace(DEFAULT_SETTINGS, sell_share=0.03, sell_ratio=2.0),
    "sell 5% x2": replace(DEFAULT_SETTINGS, sell_share=0.05, sell_ratio=2.0),
    "sell 0.5% x2.5": replace(DEFAULT_SETTINGS, sell_share=0.005, sell_ratio=2.5),
    "sell 1% x2.5": replace(DEFAULT_SETTINGS, sell_share=0.01, sell_ratio=2.5),
    "sell 2% x2.5": replace(DEFAULT_SETTINGS, sell_share=0.02, sell_ratio=2.5),
}


# but : jouer une partie avec une variante dans une classe, et renvoyer notre place et notre note
def play_one_job(job: tuple[str, str, int, int]) -> tuple[str, str, int, str]:
    variant_name, class_name, seed, rounds = job
    settings = VARIANTS[variant_name]

    def make_players() -> list[Player]:
        return CLASSES[class_name](settings)

    ranking = play_game(make_players, rounds, seed)
    for place_index, (points, gold, name) in enumerate(ranking):
        if name == OUR_NAME:
            return variant_name, class_name, place_index + 1, grade_for(place_index, len(ranking), points)
    raise ValueError("we are missing from the ranking")


# but : résumer une liste de notes, par exemple "A3 B5 C8 D4"
def grade_summary(grade_list: list[str]) -> str:
    parts = []
    for grade in ["A", "B", "C", "D", "E", "F"]:
        count = grade_list.count(grade)
        if count > 0:
            parts.append(f"{grade}{count}")
    return " ".join(parts)


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="make tournament")
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--rounds", type=int, default=1000)
    parser.add_argument("--first-seed", type=int, default=1)
    parser.add_argument("--output", default="results/tournament.md")
    parser.add_argument("--variants", default="", help="comma separated names, all variants if empty")
    values = parser.parse_args(arguments)

    selected = list(VARIANTS)
    if values.variants != "":
        selected = []
        for variant_name in values.variants.split(","):
            if variant_name.strip() not in VARIANTS:
                parser.error(f"unknown variant: {variant_name.strip()}")
            selected.append(variant_name.strip())

    jobs = []
    for variant_name in selected:
        for class_name in CLASSES:
            for seed in range(values.first_seed, values.first_seed + values.games):
                jobs.append((variant_name, class_name, seed, values.rounds))

    print(f"{len(jobs)} games on {os.cpu_count()} cores...")
    # chaque partie est indépendante : on en joue une par cœur en même temps
    with Pool() as pool:
        results = pool.map(play_one_job, jobs)

    places = {}
    grades = {}
    for variant_name, class_name, place, grade in results:
        places.setdefault((variant_name, class_name), []).append(place)
        grades.setdefault((variant_name, class_name), []).append(grade)

    lines = [f"| variant | {' | '.join(CLASSES)} | average |", "|---" * (len(CLASSES) + 2) + "|"]
    for variant_name in selected:
        cells = []
        averages = []
        for class_name in CLASSES:
            average_place = mean(places[(variant_name, class_name)])
            averages.append(average_place)
            cells.append(f"{average_place:.1f} ({grade_summary(grades[(variant_name, class_name)])})")
        lines.append(f"| {variant_name} | {' | '.join(cells)} | {mean(averages):.1f} |")

    table = "\n".join(lines)
    print(table)
    output = Path(values.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f"# Tournament\n\n"
        f"Raw output of `make tournament`, one step in choosing the settings for `expected_results.md`.\n\n"
        f"{values.games} games per class, {values.rounds} rounds, "
        f"seeds {values.first_seed} to {values.first_seed + values.games - 1}. "
        f"Average place of our agent out of 20 (lower is better), then the grade counts.\n\n{table}\n"
    )


if __name__ == "__main__":
    main()
