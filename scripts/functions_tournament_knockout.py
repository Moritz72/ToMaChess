from typing import Sequence, cast
from .parameter_armageddon import Parameter_Armageddon
from .variable_knockout_standings import Variable_Knockout_Standings


def div(a: float, b: float) -> float:
    if a % b == 0:
        return a // b - 1
    return a // b


def calculate_number_of_games(
        score_loser: Sequence[float], games: int, games_per_tiebreak: int,
        armageddon: Parameter_Armageddon, total: Sequence[float], total_tb: Sequence[float]
) -> int:
    if list(score_loser) < [t / 2 for t in total]:
        return min(int(games * (.5 + score / t) + 1) for score, t in zip(score_loser, total))
    divs, mods = tuple(zip(*(divmod(score - t / 2, t_tb / 2) for score, t, t_tb in zip(score_loser, total, total_tb))))
    estimate = games + games_per_tiebreak * int(min(divs))
    remainder = min(int(games_per_tiebreak * (.5 + mod / t_tb) + 1) for mod, t_tb in zip(mods, total_tb))
    if not armageddon.is_armageddon(games, games_per_tiebreak, estimate + remainder):
        return estimate + remainder
    if games_per_tiebreak == 1 and armageddon.is_armageddon(games, games_per_tiebreak, int(estimate + remainder - .5)):
        return estimate + remainder - 1
    return estimate + 1


def is_win(
        score: Sequence[float], score_sum: Sequence[float], games: int, games_per_tiebreak: int,
        armageddon: Parameter_Armageddon, total: Sequence[float], total_tb: Sequence[float], black: bool
) -> bool:
    score_tb = [
        sc - t / 2 - t_tb / 2 * div(sc_sum - t, t_tb) for sc, sc_sum, t, t_tb in zip(score, score_sum, total, total_tb)
    ]
    win = list(score_sum) <= list(total) and list(score) > [t / 2 for t in total]
    win_tiebreak = list(score_sum) > list(total) and score_tb > [t_tb / 2 for t_tb in total_tb]
    win_armageddon = armageddon.is_armageddon(games, games_per_tiebreak, int(score_sum[0])) and score_tb[0] + black >= 1
    return win or win_tiebreak or win_armageddon


def move_on(uuid_1: str, uuid_2: str, standings: Variable_Knockout_Standings) -> None:
    seed_1, seed_2 = standings[uuid_1].seed, standings[uuid_2].seed
    standings[uuid_1].level += 1
    standings[uuid_1].score = len(standings[uuid_1].score) * [0.]
    standings[uuid_2].beaten_by_seed = seed_1
    standings[uuid_1].seed = min(seed_1, seed_2)


def move_back(
        uuid_1: str, uuid_2: str, standings: Variable_Knockout_Standings, games: int, games_per_tiebreak: int,
        armageddon: Parameter_Armageddon, total: Sequence[float], total_tb: Sequence[float]
) -> None:
    score_loser = standings[uuid_1].score
    n_games = calculate_number_of_games(score_loser, games, games_per_tiebreak, armageddon, total, total_tb)
    standings[uuid_2].level -= 1
    standings[uuid_2].score = [n_games * t / games - score for score, t in zip(score_loser, total)]
    standings[uuid_2].seed = cast(int, standings[uuid_1].beaten_by_seed)
    standings[uuid_1].beaten_by_seed = None


def update_participant_standings(
        uuid_1: str, uuid_2: str, score_1: Sequence[float], score_2: Sequence[float],
        standings: Variable_Knockout_Standings, games: int, games_per_tiebreak: int, armageddon: Parameter_Armageddon,
        total: Sequence[float], total_tb: Sequence[float]
) -> None:
    standings[uuid_1].add_score(score_1)
    standings[uuid_2].add_score(score_2)
    total_score_1, total_score_2 = standings[uuid_1].score, standings[uuid_2].score
    total_score_sum = [score_1 + score_2 for score_1, score_2 in zip(total_score_1, total_score_2)]
    if is_win(total_score_1, total_score_sum, games, games_per_tiebreak, armageddon, total, total_tb, False):
        move_on(uuid_1, uuid_2, standings)
    elif is_win(total_score_2, total_score_sum, games, games_per_tiebreak, armageddon, total, total_tb, True):
        move_on(uuid_2, uuid_1, standings)


def reverse_participant_standings(
        uuid_1: str, uuid_2: str, score_1: Sequence[float], score_2: Sequence[float],
        standings: Variable_Knockout_Standings, games: int, games_per_tiebreak: int, armageddon: Parameter_Armageddon,
        total: Sequence[float], total_tb: Sequence[float]
) -> None:
    if standings[uuid_1].was_beaten():
        move_back(uuid_1, uuid_2, standings, games, games_per_tiebreak, armageddon, total, total_tb)
    elif standings[uuid_2].was_beaten():
        move_back(uuid_2, uuid_1, standings, games, games_per_tiebreak, armageddon, total, total_tb)
    standings[uuid_1].add_score(score_1, reverse=True)
    standings[uuid_2].add_score(score_2, reverse=True)


def get_end_rounds(
        standings_dict: Variable_Knockout_Standings, games: int, games_per_tiebreak: int,
        armageddon: Parameter_Armageddon, total: Sequence[float], total_tb: Sequence[float]
) -> list[int]:
    levels_max: dict[int, list[float]] = dict()
    for standing in standings_dict.values():
        if standing.level not in levels_max or levels_max[standing.level] < standing.score:
            levels_max[standing.level] = standing.score
    return [
        calculate_number_of_games(max_score, games, games_per_tiebreak, armageddon, total, total_tb)
        for _, max_score in sorted(levels_max.items())
    ]
