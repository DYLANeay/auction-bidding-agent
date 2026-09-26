"""The buyer who uses every tool in order each round (think: the driver reading the dashboard)"""

from smaug.agent.config import DEFAULT_SETTINGS, Settings
from smaug.agent.strategy.bidding import choose_bids
from smaug.agent.strategy.market import market_price, round_price_per_point
from smaug.agent.strategy.planning import current_margin, reserve, spending_budget


class Brain:
    """Remembers recent market prices and turns each round into bids"""

    def __init__(self, settings: Settings = DEFAULT_SETTINGS) -> None:
        self.settings = settings
        self.price_history: list[float] = []

    def remember_prices(self, prev_auctions: dict[str, dict]) -> None:
        price = round_price_per_point(prev_auctions, self.settings.min_expected_value)
        if price is None:
            return
        self.price_history.append(price)
        # fenêtre glissante : on oublie les tours trop anciens
        while len(self.price_history) > self.settings.history_rounds:
            self.price_history.pop(0)

    def decide(
        self,
        gold: float,
        auctions: dict[str, dict],
        prev_auctions: dict[str, dict],
        bank_state: dict[str, list],
    ) -> dict[str, int]:
        self.remember_prices(prev_auctions)

        rounds_left = len(bank_state["gold_income_per_round"])
        # tour fantôme : jamais traité par le serveur, inutile de miser
        if rounds_left <= 1:
            return {}

        bank_limit = bank_state["bank_limit_per_round"][0]
        savings = reserve(bank_limit, rounds_left, self.settings)
        budget = spending_budget(gold, savings)
        price = market_price(self.price_history, self.settings.default_price)
        margin = current_margin(rounds_left, self.settings)
        is_last_useful_round = rounds_left == 2

        return choose_bids(auctions, budget, price, margin, self.settings, is_last_useful_round)
