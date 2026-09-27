"""The scorecard counts our won and lost bids, and the gold lost"""

from smaug.agent.report import last_round_results


def auction_with(bids: list[tuple[str, int]]) -> dict:
    return {"die": 6, "num": 2, "bonus": 0, "bids": [{"a_id": a_id, "gold": gold} for a_id, gold in bids]}


def test_our_highest_bid_wins() -> None:
    prev_auctions = {"a1": auction_with([("me", 100), ("other", 80)])}
    assert last_round_results(prev_auctions, "me") == {"won": 1, "lost": 0, "gold_lost": 0}


def test_a_lost_bid_costs_the_half_not_given_back() -> None:
    prev_auctions = {"a1": auction_with([("other", 200), ("me", 101)])}
    # le serveur rend int(101 * 0.5) = 50, on perd donc 51
    assert last_round_results(prev_auctions, "me") == {"won": 0, "lost": 1, "gold_lost": 51}


def test_a_tie_on_top_counts_as_lost() -> None:
    prev_auctions = {"a1": auction_with([("other", 100), ("me", 100)])}
    assert last_round_results(prev_auctions, "me")["lost"] == 1


def test_auctions_we_did_not_bid_on_are_ignored() -> None:
    prev_auctions = {"a1": auction_with([("other", 100)]), "a2": auction_with([])}
    assert last_round_results(prev_auctions, "me") == {"won": 0, "lost": 0, "gold_lost": 0}
