def div(a, b):
    if a % b == 0:
        return a // b - 1
    return a // b


def calculate_number_of_games(score_loser, games, games_per_tiebreak, armageddon, total, total_tb):
    if score_loser < [t / 2 for t in total]:
        return min(int(games * (.5 + score / t) + 1) for score, t in zip(score_loser, total))
    divs, mods = tuple(zip(*(divmod(score - t / 2, t_tb / 2) for score, t, t_tb in zip(score_loser, total, total_tb))))
    estimate = games + games_per_tiebreak * int(min(divs))
    remainder = min(int(games_per_tiebreak * (.5 + mod / t_tb) + 1) for mod, t_tb in zip(mods, total_tb))
    if not armageddon.is_armageddon(games, games_per_tiebreak, estimate + remainder):
        return estimate + remainder
    if games_per_tiebreak == 1 and armageddon.is_armageddon(games, games_per_tiebreak, estimate + remainder - .5):
        return estimate + remainder - 1
    return estimate + 1


def is_win(score, score_sum, games, games_per_tiebreak, armageddon, total, total_tb, black):
    score_in_tb = [
        sc - t / 2 - t_tb / 2 * div(sc_sum - t, t_tb) for sc, sc_sum, t, t_tb in zip(score, score_sum, total, total_tb)
    ]
    win = score_sum <= total and score > [t / 2 for t in total]
    win_tiebreak = score_sum > total and score_in_tb > [t_tb / 2 for t_tb in total_tb]
    win_armageddon = armageddon.is_armageddon(games, games_per_tiebreak, score_sum[0]) and score_in_tb[0] + black >= 1
    return win or win_tiebreak or win_armageddon


def add_score_to_participant_standings(uuid, score, participant_standings, r=1):
    participant_standings[uuid]["score"] = [
        sc_current + r * sc for sc_current, sc in zip(participant_standings[uuid]["score"], score)
    ]


def move_on(uuid_1, uuid_2, participant_standings):
    seating_1, seating_2 = participant_standings[uuid_1]["seating"], participant_standings[uuid_2]["seating"]
    participant_standings[uuid_1]["level"] += 1
    participant_standings[uuid_1]["score"] = len(participant_standings[uuid_1]["score"]) * [0]
    participant_standings[uuid_2]["beaten_by_seat"] = seating_1
    participant_standings[uuid_1]["seating"] = min(seating_1, seating_2)


def move_back(uuid_1, uuid_2, participant_standings, games, games_per_tiebreak, armageddon, total, total_tb):
    score_loser = participant_standings[uuid_1]["score"]
    n_games = calculate_number_of_games(score_loser, games, games_per_tiebreak, armageddon, total, total_tb)
    participant_standings[uuid_2]["level"] -= 1
    participant_standings[uuid_2]["score"] = [n_games * t / games - score for score, t in zip(score_loser, total)]
    participant_standings[uuid_2]["seating"] = participant_standings[uuid_1]["beaten_by_seat"]
    participant_standings[uuid_1]["beaten_by_seat"] = None


def update_participant_standings(
        uuid_1, uuid_2, score_1, score_2, participant_standings, games, games_per_tiebreak, armageddon, total, total_tb
):
    add_score_to_participant_standings(uuid_1, score_1, participant_standings)
    add_score_to_participant_standings(uuid_2, score_2, participant_standings)
    total_score_1, total_score_2 = participant_standings[uuid_1]["score"], participant_standings[uuid_2]["score"]
    total_score_sum = [score_1 + score_2 for score_1, score_2 in zip(total_score_1, total_score_2)]
    if is_win(total_score_1, total_score_sum, games, games_per_tiebreak, armageddon, total, total_tb, False):
        move_on(uuid_1, uuid_2, participant_standings)
    elif is_win(total_score_2, total_score_sum, games, games_per_tiebreak, armageddon, total, total_tb, True):
        move_on(uuid_2, uuid_1, participant_standings)


def reverse_participant_standings(
        uuid_1, uuid_2, score_1, score_2, participant_standings, games, games_per_tiebreak, armageddon, total, total_tb
):
    if participant_standings[uuid_1]["beaten_by_seat"] is not None:
        move_back(uuid_1, uuid_2, participant_standings, games, games_per_tiebreak, armageddon, total, total_tb)
    elif participant_standings[uuid_2]["beaten_by_seat"] is not None:
        move_back(uuid_2, uuid_1, participant_standings, games, games_per_tiebreak, armageddon, total, total_tb)
    add_score_to_participant_standings(uuid_1, score_1, participant_standings, r=-1)
    add_score_to_participant_standings(uuid_2, score_2, participant_standings, r=-1)


def get_end_rounds(participant_standings, games, games_per_tiebreak, armageddon, total, total_tb):
    levels_max = dict()
    for standing in participant_standings.values():
        if standing["level"] not in levels_max or levels_max[standing["level"]] < standing["score"]:
            levels_max[standing["level"]] = standing["score"]
    return [
        calculate_number_of_games(max_score, games, games_per_tiebreak, armageddon, total, total_tb)
        for _, max_score in sorted(levels_max.items())
    ]


def get_current_level(participant_standings):
    min_level = None
    for standing in participant_standings.values():
        if standing["beaten_by_seat"] is None and (min_level is None or standing["level"] < min_level):
            min_level = standing["level"]
    return min_level


def get_uuids_in_current_level(participant_standings):
    current_level = get_current_level(participant_standings)
    uuids_and_standings = [
        (uuid, standing) for uuid, standing in participant_standings.items()
        if standing["beaten_by_seat"] is None and standing["level"] == current_level
    ]
    return sorted(
        [uuid for uuid, standing in uuids_and_standings if standing["level"] >= current_level],
        key=lambda x: participant_standings[x]["seating"]
    )
