"""One round whose data has all been checked (think: a checked boarding pass)"""

from dataclasses import dataclass


# un tour dont chaque donnée a été vérifiée, prêt pour le cerveau
@dataclass
class Round:
    gold: int
    auctions: dict[str, dict]
    prev_auctions: dict[str, dict]
    bank_state: dict[str, list]
