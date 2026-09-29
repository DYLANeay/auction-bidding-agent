"""Checks for instructions left in control.json before a game starts (think: a sticky note left from the last flight)"""

import json
from collections.abc import Callable
from pathlib import Path

MAX_SHOWN_CHARACTERS = 200


# but : savoir si control.json demande encore quelque chose au démarrage, sans jamais planter
def leftover_instructions(path: Path) -> str | None:
    """What the file still asks for, or None if it is missing or empty"""
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (OSError, ValueError):
        return None
    if text == "":
        return None
    # sur une seule ligne, pour tenir dans la question
    shown = " ".join(text.split())[:MAX_SHOWN_CHARACTERS]
    try:
        instructions = json.loads(text)
    except (ValueError, RecursionError):
        # illisible : on le montre tel quel, c'est justement suspect
        return shown
    if instructions == {}:
        return None
    return shown


# but : effacer une consigne oubliée, sauf si on demande explicitement de la garder
def clear_unless_kept(path: Path, leftover: str | None, ask: Callable[[str], str]) -> bool:
    """True if the leftover instructions were cleared"""
    if leftover is None:
        return False
    try:
        answer = ask(f"logs/control.json still asks for {leftover}. Keep it for this game? (y/N) ")
    except EOFError:
        # lancé sans clavier (make rehearsal) : personne ne peut répondre, on efface
        answer = ""
    if answer.strip().lower() in ["y", "yes", "o", "oui"]:
        return False
    try:
        path.write_text("{}", encoding="utf-8")
    except OSError:
        return False
    return True
