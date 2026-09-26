"""Checks everything going in and out of the brain (think: airport security)"""

import math
from typing import Any

from smaug.agent.brain import Brain

#
#  Brain ──▶ [clean_bids + to_whole_number] ──▶ serveur
# « est-ce vraiment un nombre utilisable ? »


# but : transformer n'importe quelle valeur en nombre à virgule sûr, ou dire qu'elle est inutilisable
def to_number(value: Any) -> float | None:
    """A finite float from any number, or None if it is not a usable number"""
    # True et False sont des nombres pour Python, jamais pour nous
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    # rejette NaN et l'infini
    if not math.isfinite(number):
        return None
    return number


def to_whole_number(value: Any) -> int | None:
    """A plain Python int from any number, or None if it is not a usable number"""
    number = to_number(value)
    if number is None:
        return None
    return int(number)


# « ne laisser partir que des mises valides »
def clean_bids(raw_bids: object, auction_ids: set[str], gold: int) -> dict[str, int]:
    """Only valid bids: Python ints of at least 1, on this round's auctions, within our gold"""
    if not isinstance(raw_bids, dict):
        return {}

    cleaned = {}
    remaining = gold
    for auction_id, raw_bid in raw_bids.items():
        if auction_id not in auction_ids:
            continue
        bid = to_whole_number(raw_bid)
        if bid is None or bid < 1:
            continue
        # le serveur ignore en silence une mise qui dépasse l'or restant
        if bid > remaining:
            continue
        cleaned[auction_id] = bid
        remaining -= bid
    return cleaned


# demande ses mises au cerveau dans une zone protégée : si le cerveau plante, on saute le tour, et s'il répond, on nettoie sa réponse avant de l'envoyer
def safe_decide(
    brain: Brain,
    gold: int,
    auctions: dict[str, dict],
    prev_auctions: dict[str, dict],
    bank_state: dict[str, list],
) -> dict[str, int]:
    """The brain's bids, cleaned, or no bids at all if anything goes wrong"""
    try:
        raw_bids = brain.decide(gold, auctions, prev_auctions, bank_state)
    except Exception:  # noqa: BLE001
        # un bug dans le cerveau ne doit jamais arrêter l'agent : on saute le tour
        return {}
    return clean_bids(raw_bids, set(auctions), gold)


# au-delà, les dés ne peuvent venir que d'un message piégé
MAX_DIE = 1000
MAX_DICE = 1000
MAX_BONUS = 10000


# but : lire les dés d'une enchère et refuser ceux qui sont absents, cassés ou absurdes
def read_auction(raw: Any) -> dict[str, int] | None:
    """Dice of one auction, or None if they make no sense"""
    if not isinstance(raw, dict):
        return None
    die = to_whole_number(raw.get("die"))
    num = to_whole_number(raw.get("num"))
    bonus = to_whole_number(raw.get("bonus"))
    if die is None or num is None or bonus is None:
        return None
    if die < 1 or die > MAX_DIE:
        return None
    if num < 1 or num > MAX_DICE:
        return None
    if abs(bonus) > MAX_BONUS:
        return None
    return {"die": die, "num": num, "bonus": bonus}


# but : donner le montant d'une mise, pour pouvoir trier les mises par or
def bid_gold(bid: dict) -> int:
    return bid["gold"]


# but : lire les mises d'une enchère terminée, retirer les cassées et remettre la plus haute en premier
def read_bids(raw_bids: Any) -> list[dict]:
    """Bids of a finished auction, highest first, without the broken ones"""
    if not isinstance(raw_bids, list):
        return []
    bids = []
    for raw_bid in raw_bids:
        if not isinstance(raw_bid, dict):
            continue
        gold = to_whole_number(raw_bid.get("gold"))
        if gold is None or gold < 0:
            continue
        bids.append({"a_id": str(raw_bid.get("a_id", "")), "gold": gold})
    # on ne fait pas confiance à l'ordre reçu : la plus haute mise d'abord
    bids.sort(key=bid_gold, reverse=True)
    return bids


# but : lire toutes les enchères du tour en ignorant seulement celles qui sont cassées
def read_auctions(raw: Any) -> dict[str, dict]:
    """This round's auctions, skipping the broken ones"""
    if not isinstance(raw, dict):
        return {}
    auctions = {}
    for auction_id, raw_auction in raw.items():
        auction = read_auction(raw_auction)
        if isinstance(auction_id, str) and auction is not None:
            auctions[auction_id] = auction
    return auctions


# but : lire les résultats du tour précédent (dés + mises) en ignorant ceux qui sont cassés
def read_prev_auctions(raw: Any) -> dict[str, dict]:
    """Last round's results with their bids, skipping the broken ones"""
    if not isinstance(raw, dict):
        return {}
    prev_auctions = {}
    for auction_id, raw_auction in raw.items():
        auction = read_auction(raw_auction)
        if not isinstance(auction_id, str) or auction is None:
            continue
        prev_auctions[auction_id] = {
            "die": auction["die"],
            "num": auction["num"],
            "bonus": auction["bonus"],
            "bids": read_bids(raw_auction.get("bids")),
        }
    return prev_auctions


# but : lire une liste de nombres, et la refuser entièrement au moindre élément cassé
def read_number_list(raw: Any) -> list[float] | None:
    """A non-empty list of usable numbers, or None"""
    if not isinstance(raw, list) or len(raw) == 0:
        return None
    numbers = []
    for raw_value in raw:
        number = to_number(raw_value)
        if number is None:
            return None
        numbers.append(number)
    return numbers


# but : assembler le futur de la banque (salaires, taux, plafonds) au format du cerveau, ou refuser le tour
def read_bank_state(message: dict) -> dict[str, list] | None:
    """The bank's future from the server message, or None if any part is broken"""
    gold_income = read_number_list(message.get("remainder_gold_income"))
    bank_interest = read_number_list(message.get("remainder_bank_interest"))
    bank_limit = read_number_list(message.get("remainder_bank_limit"))
    if gold_income is None or bank_interest is None or bank_limit is None:
        return None
    if bank_limit[0] < 0:
        return None
    return {
        "gold_income_per_round": gold_income,
        "bank_interest_per_round": bank_interest,
        "bank_limit_per_round": bank_limit,
    }


# but : retrouver notre or parmi l'état de tous les joueurs, ou refuser le tour si on ne le trouve pas
def read_gold(states: Any, agent_id: str) -> int | None:
    """Our own gold from the players' states, or None if we cannot find it"""
    if not isinstance(states, dict):
        return None
    our_state = states.get(agent_id)
    if not isinstance(our_state, dict):
        return None
    gold = to_whole_number(our_state.get("gold"))
    if gold is None or gold < 0:
        return None
    return gold
