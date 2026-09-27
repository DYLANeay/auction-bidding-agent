#!/usr/bin/env bash
# a full local game in one command: teacher's server, example opponents, our agent, then the gong
# usage: scripts/local_game.sh [rounds] [opponents]
set -euo pipefail

ROUNDS="${1:-300}"
OPPONENTS="${2:-5}"
LOGS=logs/rehearsal
EXAMPLES=context/dnd_auction_game/example_agents
BOARD=http://localhost:8000/api/leadboard

# lit une info du tableau des scores
board() {
  curl -s "$BOARD" | python3 -c "import sys, json; board = json.load(sys.stdin); print($1)"
}

# les agents d'exemple du prof sont codés en dur sur le port 8000
if curl -s "$BOARD" > /dev/null; then
  echo "A server is already running on port 8000, stop it first."
  exit 1
fi

mkdir -p "$LOGS"
# à la sortie (fin normale ou Ctrl+C), on arrête tout ce qu'on a lancé
trap 'kill $(jobs -p) 2> /dev/null; wait 2> /dev/null' EXIT

echo "Starting the teacher's server"
AH_LOG_DIR="$LOGS" uv run python -m dnd_auction_game.server > "$LOGS/server.txt" 2>&1 &
until curl -s "$BOARD" > /dev/null; do sleep 0.5; done

echo "Seating $OPPONENTS opponents and our agent"
agents=(agent_tiny_bid agent_random_single agent_random_walk)
for i in $(seq 1 "$OPPONENTS"); do
  # -B : jamais de __pycache__ dans context/
  uv run python -B "$EXAMPLES/${agents[$((i % 3))]}.py" >> "$LOGS/opponents.txt" 2>&1 &
done
# en local quoi que dise .env
uv run python -m smaug.agent.connection.run --host localhost --port 8000 --token play123 > "$LOGS/agent.txt" 2>&1 &

# le gong seulement quand tout le monde est assis
waited=0
until [ "$(board 'len(board["players"])')" -ge $((OPPONENTS + 1)) ]; do
  sleep 1
  waited=$((waited + 1))
  if [ "$waited" -ge 60 ]; then
    echo "Not everyone could connect, see $LOGS/"
    exit 1
  fi
done

echo "Gong: $ROUNDS rounds, follow the game on http://localhost:8000"
uv run python -m dnd_auction_game.play "$ROUNDS" > /dev/null

until [ "$(board 'board["is_done"]')" = "True" ]; do
  sleep 5
  echo "  round $(board 'board["round"]') / $ROUNDS"
done

echo
echo "Final ranking"
curl -s "$BOARD" | python3 -c '
import sys, json
for player in json.load(sys.stdin)["players"]:
    print(player["grade"], player["points"], player["name"], sep="\t")
'
echo
echo "Agent: $(tail -n 1 "$LOGS/agent.txt")"
