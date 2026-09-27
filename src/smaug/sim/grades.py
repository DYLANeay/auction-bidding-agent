"""The grade of a place in the ranking, exactly like the server (think: the teacher's grading scale)"""


# but : donner la note d'une place comme le serveur (server.py, lignes 149 à 163)
def grade_for(place_index: int, player_count: int, points: int) -> str:
    if points <= 10:
        return "F"
    rank_fraction = (player_count - place_index) / player_count
    if rank_fraction > 0.89:
        return "A"
    if rank_fraction > 0.75:
        return "B"
    if rank_fraction > 0.60:
        return "C"
    if rank_fraction > 0.40:
        return "D"
    return "E"
