"""Default settings of the agent (think: the dashboard knobs in their factory position)"""

from dataclasses import dataclass


# similar as an interface but with default values for the agent's configuration parameters
@dataclass(frozen=True)
class Settings:
    min_expected_value: float = 2.0
    history_rounds: int = 20
    margin: float = 0.15
    reserve_factor: float = 1.0  # share of the bank limit kept as savings
    endgame_rounds: int = 50
    default_price: float = 20.0  # gold per point, only used before any history


DEFAULT_SETTINGS = Settings()
