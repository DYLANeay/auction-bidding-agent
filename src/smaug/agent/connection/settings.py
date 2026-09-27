"""Where and how to reach the server (think: the phone's address book)"""

import argparse
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ConnectionSettings:
    host: str
    port: int
    token: str
    name: str
    player_id: str


# but : lire les réglages de connexion, en priorité dans les arguments, sinon dans l'environnement (.env)
def read_connection_settings(arguments: list[str]) -> ConnectionSettings:
    parser = argparse.ArgumentParser(prog="make battle")
    parser.add_argument("--host", default=os.environ.get("AH_HOST", "localhost"))
    # argparse convertit aussi la valeur par défaut : un AH_PORT invalide donne un message clair
    parser.add_argument("--port", type=int, default=os.environ.get("AH_PORT", "8000"))
    parser.add_argument("--token", default=os.environ.get("AH_TOKEN", "play123"))
    parser.add_argument("--name", default=os.environ.get("AH_NAME", "Smaug"))
    parser.add_argument("--player-id", default=os.environ.get("AH_PLAYER_ID", "unknown"))
    values = parser.parse_args(arguments)

    # le serveur refuse un nom de moins de 2 ou plus de 64 caractères
    if len(values.name) < 2 or len(values.name) > 64:
        parser.error("the name must be between 2 and 64 characters")

    return ConnectionSettings(values.host, values.port, values.token, values.name, values.player_id)
