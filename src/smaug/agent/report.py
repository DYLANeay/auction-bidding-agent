"""What happened to our bids last round (think: the scorecard after each hand)"""

# un perdant récupère la moitié de sa mise (auction_house.py ligne 146)
GOLD_BACK_FRACTION = 0.5


def our_bid(bids: list[dict], agent_id: str) -> int | None:
    for bid in bids:
        if bid["a_id"] == agent_id:
            return bid["gold"]
    return None


def count_bids_at(bids: list[dict], gold: int) -> int:
    count = 0
    for bid in bids:
        if bid["gold"] == gold:
            count += 1
    return count


def last_round_results(prev_auctions: dict[str, dict], agent_id: str) -> dict[str, int]:
    """How many of our bids won and lost last round, and the gold the lost ones cost"""
    won = 0
    lost = 0
    gold_lost = 0
    for auction in prev_auctions.values():
        bids = auction["bids"]
        gold = our_bid(bids, agent_id)
        if gold is None:
            continue
        top_gold = bids[0]["gold"]
        # égalité au sommet : une priorité secrète décide, on la compte comme perdue
        if gold == top_gold and count_bids_at(bids, top_gold) == 1:
            won += 1
        else:
            lost += 1
            gold_lost += gold - int(gold * GOLD_BACK_FRACTION)
    return {"won": won, "lost": lost, "gold_lost": gold_lost}
