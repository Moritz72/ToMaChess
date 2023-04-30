from .functions_util import recursive_buckets, shorten_float


def get_score_dict_by_point_system(point_system):
    win, draw, loss = point_system.split(' - ')
    if draw == '½':
        draw = '.5'
    win = shorten_float(float(win))
    draw = shorten_float(float(draw))
    loss = shorten_float(float(loss))
    return {'1': win, '½': draw, '0': loss, '+': win, '-': loss}


def get_standings_header_vertical(table):
    header_vertical = []
    last_entry = None
    for i, entry in enumerate(table):
        if last_entry is None or entry[1:] != last_entry[1:]:
            header_vertical.append(str(i+1))
        else:
            header_vertical.append('')
        last_entry = entry
    return header_vertical


def get_standings_with_tiebreaks(tournament, tiebreak_args):
    uuid_to_participant_dict = tournament.get_uuid_to_participant_dict()
    tiebreaks = []
    i = 1
    while True:
        try:
            tiebreaks.append(tournament.get_parameter(f"tiebreak {i}"))
            i += 1
        except:
            break

    header_horizontal = ["Name", "P"]
    rank_functions = [lambda x: tournament.get_simple_scores()]
    for tb in tiebreaks:
        if tb.get_abbreviation() is None:
            continue
        header_horizontal.append(tb.get_abbreviation())
        rank_functions.append(lambda x, tiebreak=tb: tiebreak.evaluate({"uuids": x} | tiebreak_args))

    table = [
        [uuid_to_participant_dict[e[0]]] + e[1:]
        for e in recursive_buckets([[e] for e in uuid_to_participant_dict], rank_functions)
    ]

    return header_horizontal, get_standings_header_vertical(table), table


def get_team_result(individual_results, results_dict):
    if all(score_1 == '-' and score_2 == '-' for (_, score_1), (_, score_2) in individual_results):
        return '-', '-'
    if all(score_1 == '-' for (_, score_1), (_, _) in individual_results):
        return '-', '+'
    if all(score_2 == '-' for (_, _), (_, score_2) in individual_results):
        return '+', '-'
    sum_1 = sum(results_dict[score_1] for (_, score_1), (_, _) in individual_results)
    sum_2 = sum(results_dict[score_2] for (_, _), (_, score_2) in individual_results)
    if sum_1 > sum_2:
        return '1', '0'
    if sum_2 > sum_1:
        return '0', '1'
    return '½', '½'


def is_valid_team_seatings(team_uuids, team_member_lists, results_match):
    indices = [0, 0]
    for result in results_match:
        for i, ((uuid, _), index, team_member_list) in enumerate(zip(result, indices, team_member_lists)):
            if uuid is None:
                indices[i] = None
                continue
            number = team_member_list.index(uuid) + 1
            if index is None or number <= index:
                return False
            indices[i] = number
    return True
