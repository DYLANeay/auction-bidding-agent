"""Default settings of the agent (think: the dashboard knobs in their factory position)"""

from dataclasses import dataclass


# comme une interface, mais avec des valeurs par défaut pour les réglages de l'agent
@dataclass(frozen=True)
class Settings:
    min_expected_value: float = 2.0  # ignore les enchères qui rapportent moins que ça en moyenne
    history_rounds: int = 20  # fenêtre glissante pour le prix du marché
    margin: float = 0.15  # on mise le prix du marché plus 15 %
    reserve_factor: float = 1.0  # part du plafond de la banque gardée en épargne
    endgame_rounds: int = 100  # l'épargne fond pendant ces derniers tours utiles
    endgame_finish_rounds: int = 10  # l'épargne est à zéro ce nombre de tours avant la fin, avant le pic
    endgame_margin: float = 0.60  # en fin de partie : gros coups, on paie plus cher pour gagner à coup sûr
    default_price: float = 20.0  # or par point, utilisé seulement avant tout historique


DEFAULT_SETTINGS = Settings()
