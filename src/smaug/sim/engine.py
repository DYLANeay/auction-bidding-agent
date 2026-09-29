"""One full game offline with the teacher's engine, in the order of the real server (think: the flight simulator)"""

import json
import random
from collections.abc import Callable

from dnd_auction_game.auction_house import AuctionHouse

from smaug.sim.players import Player, ask_player


# but : jouer une partie complète hors ligne et renvoyer le classement (points, or, nom), du meilleur au moins bon
def play_game(make_players: Callable[[], list[Player]], rounds: int, seed: int) -> list[tuple[int, int, str]]:
    # tout le hasard (moteur du prof et joueurs, dès leur création) part de la graine : même graine, même partie
    random.seed(seed)
    players = make_players()
    house = AuctionHouse("game", "play", save_logs=False)
    for number, player in enumerate(players):
        house.add_agent(player.name, f"agent_{number}", "simulation", f"secret-{number}")
    house.set_num_rounds(rounds)
    house.assign_priorities()

    while True:
        # le même ordre que le serveur (server.py, lignes 221 à 256)
        published_rate = house.gold_per_point
        house.process_all_bids()
        house.process_point_purchases(published_rate)
        state = house.prepare_auctions()
        if house.round_counter >= rounds:
            # le tour fantôme n'est jamais traité
            break
        text = json.dumps(state)
        for number, player in enumerate(players):
            agent_id = f"agent_{number}"
            answer = ask_player(player, text, agent_id)
            if not isinstance(answer, dict):
                continue
            # comme le serveur (server.py ligne 369) : la vente de points, puis les mises
            house.register_point_purchase(agent_id, answer.get("points_to_spend", 0))
            bids = answer.get("bids", {})
            if not isinstance(bids, dict):
                continue
            for auction_id, gold in bids.items():
                house.register_bid(agent_id, auction_id, gold)

    ranking = []
    for number, player in enumerate(players):
        state = house.agents[f"agent_{number}"]
        ranking.append((state["points"], state["gold"], player.name))
    ranking.sort(reverse=True)
    return ranking
