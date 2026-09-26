"""Turns any value into a safe number or says it is unusable (think: the scanner)"""

import math
from typing import Any

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
