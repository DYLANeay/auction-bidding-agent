"""Default settings of the agent (think: the dashboard knobs in their factory position)"""

from dataclasses import dataclass


# comme une interface, mais avec des valeurs par défaut pour les réglages de l'agent
@dataclass(frozen=True)
class Settings:
    min_expected_value: float = 8.0  # ignore les enchères qui rapportent moins que ça en moyenne
    history_rounds: int = 10  # fenêtre glissante pour le prix du marché
    margin: float = 0.30  # on mise le prix du marché plus 30 %
    reserve_factor: float = 1.0  # part du plafond de la banque gardée en épargne
    endgame_rounds: int = 100  # l'épargne fond pendant ces derniers tours utiles
    endgame_finish_rounds: int = 10  # l'épargne est à zéro ce nombre de tours avant la fin, avant le pic
    endgame_margin: float = 0.60  # en fin de partie : gros coups, on paie plus cher pour gagner à coup sûr
    default_price: float = 20.0  # or par point, utilisé seulement avant tout historique


# réglages choisis par le tournoi (results/confirmation.md)
DEFAULT_SETTINGS = Settings()

# la toute première version, avant le tournoi, gardée pour comparer
V1_SETTINGS = Settings(min_expected_value=2.0, history_rounds=20, margin=0.15)
