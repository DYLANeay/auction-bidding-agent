"""Checks everything going in and out of the brain (think: airport security)"""

import math
from typing import Any

from smaug.agent.brain import Brain

#
#  Brain ──▶ [clean_bids + to_whole_number] ──▶ serveur
# « est-ce vraiment un nombre utilisable ? »


def to_whole_number(value: Any) -> int | None:
    """A plain Python int from any number, or None if it is not a usable number"""
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
