"""The teacher's example agents, borrowed from context/ without writing anything there (think: borrowing players)"""

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from smaug.sim.players import ClassicAgent

EXAMPLES = Path(__file__).resolve().parents[3] / "context" / "dnd_auction_game" / "example_agents"


# but : charger un fichier d'agent d'exemple du prof en mémoire, sans créer de __pycache__ dans context/
def load_example(file_name: str) -> ModuleType:
    path = EXAMPLES / file_name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    was_writing_bytecode = not sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = not was_writing_bytecode
    return module


def tiny_bid(name: str) -> ClassicAgent:
    return ClassicAgent(name, load_example("agent_tiny_bid.py").tiny_bid)


def random_single(name: str) -> ClassicAgent:
    return ClassicAgent(name, load_example("agent_random_single.py").random_single_bid)


def random_walk(name: str) -> ClassicAgent:
    # chaque exemplaire a sa propre mémoire, comme dans le fichier du prof
    walker = load_example("agent_random_walk.py").RandomWalkAgent(max_move_up_or_down=10)
    return ClassicAgent(name, walker.random_walk)
