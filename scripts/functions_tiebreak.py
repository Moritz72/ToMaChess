from .functions_util import shorten_float


def shorten_floats(scores):
    return {uuid: shorten_float(score) for uuid, score in scores.items()}


def median(scores):
    half, rest = divmod(len(scores), 2)
    if half:
        return (scores[half]+scores[half+1])/2
    return scores[half]


def cut_list(lis, cut_up, cut_down, sort=True):
    while cut_up+cut_down > len(lis):
        if cut_up >= cut_down:
            cut_up -= 1
        else:
            cut_down -= 1
    if sort:
        lis = sorted(lis)
    if cut_up:
        return lis[cut_down:-cut_up]
    return lis[cut_down:]


def get_scores_corrected(results, score_dict, all_participants):
    score_default = median(list(score_dict.values()))
    scores_corrected = {participant.get_uuid(): 0 for participant in all_participants}
    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if score_1 in ('+', '-'):
                if uuid_1 is not None:
                    scores_corrected[uuid_1] += score_default
                if uuid_2 is not None:
                    scores_corrected[uuid_2] += score_default
            else:
                scores_corrected[uuid_1] += score_dict[score_1]
                scores_corrected[uuid_2] += score_dict[score_2]
    return scores_corrected


def get_scores_and_opponents_with_scores_and_virtuals(uuids, results, score_dict):
    score_default = median(list(score_dict.values()))
    scores = {uuid: 0 for uuid in uuids}
    opponents_with_scores = {uuid: [] for uuid in uuids}
    virtuals = {uuid: [] for uuid in uuids}

    for i, roun in enumerate(results):
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 in scores:
                if uuid_2 is None:
                    virtuals[uuid_1].append(scores[uuid_1]+(len(results)-i-1)*score_default)
                else:
                    opponents_with_scores[uuid_1].append((uuid_2, score_dict[score_1]))
                scores[uuid_1] += score_dict[score_1]
            if uuid_2 in scores:
                if uuid_1 is None:
                    virtuals[uuid_2].append(scores[uuid_2]+(len(results)-i-1)*score_default)
                else:
                    opponents_with_scores[uuid_2].append((uuid_1, score_dict[score_2]))
                scores[uuid_2] += score_dict[score_2]
    return scores, opponents_with_scores, virtuals


def get_buchholz(uuids, results, score_dict, all_participants, cut_up=0, cut_down=0, virtual=True):
    scores, opponents_with_scores, virtuals =\
        get_scores_and_opponents_with_scores_and_virtuals(uuids, results, score_dict)
    if not virtual:
        virtuals = {uuid: [] for uuid in virtuals}
    scores_corrected = get_scores_corrected(results, score_dict, all_participants)

    score_collections = {
        uuid: [scores_corrected[opponent] for opponent, _ in opponents_with_scores[uuid]] + virtuals[uuid]
        for uuid in uuids
    }
    return shorten_floats(
        {uuid: sum(cut_list(score_collection, cut_up, cut_down))
         for uuid, score_collection in score_collections.items()}
    )


def get_buchholz_sum(uuids, results, score_dict, all_participants, cut_up=0, cut_down=0, virtual=True):
    buchholzs = get_buchholz([participant.get_uuid() for participant in all_participants],
                             results, score_dict, all_participants, cut_up, cut_down, virtual)
    opponents = {participant.get_uuid(): [] for participant in all_participants}

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 is None or uuid_2 is None:
                continue
            opponents[uuid_1].append(uuid_2)
            opponents[uuid_2].append(uuid_1)

    score = {uuid: sum((buchholzs[opponent] for opponent in opponents[uuid])) for uuid in uuids}
    return shorten_floats(score)


def get_sonneborn_berger(uuids, results, score_dict, all_participants, cut_up=0, cut_down=0, virtual=False):
    scores, opponents_with_scores, virtuals =\
        get_scores_and_opponents_with_scores_and_virtuals(uuids, results, score_dict)
    if not virtual:
        virtuals = {uuid: [] for uuid in virtuals}
    scores_corrected = get_scores_corrected(results, score_dict, all_participants)

    score_collections = {
        uuid:
            [scores_corrected[opponent] * score for opponent, score in opponents_with_scores[uuid]] + virtuals[uuid]
        for uuid in uuids
    }
    return shorten_floats(
        {uuid: sum(cut_list(score_collection, cut_up, cut_down))
         for uuid, score_collection in score_collections.items()}
    )


def get_blacks(uuids, results):
    blacks = {uuid: 0 for uuid in uuids}

    for roun in results:
        for (uuid_1, _), (uuid_2, _) in roun:
            if uuid_1 is None or uuid_2 is None or uuid_2 not in blacks:
                continue
            blacks[uuid_2] += 1
    return blacks


def get_number_of_wins(uuids, results, score_dict, include_forfeits=True):
    score_max = max(score_dict.values())
    wins = {uuid: 0 for uuid in uuids}

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 in wins:
                if score_dict[score_1] == score_max and (include_forfeits or score_1 != '+'):
                    wins[uuid_1] += 1
            if uuid_2 in wins:
                if score_dict[score_2] == score_max and (include_forfeits or score_2 != '+'):
                    wins[uuid_2] += 1
    return wins


def get_number_of_black_wins(uuids, results, score_dict):
    black_wins = {uuid: 0 for uuid in uuids}

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 is None or uuid_2 is None or uuid_2 not in black_wins:
                continue
            if score_dict[score_2] == max(score_dict.values()):
                black_wins[uuid_2] += 1
    return black_wins


def get_opponent_average_rating(uuids, results, score_dict, all_participants, cut_up=0, cut_down=0):
    id_to_rating_dict = {participant.get_uuid(): participant.get_rating() for participant in all_participants}
    opponents_ratings = {uuid: [] for uuid in uuids}
    excluded = False

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if (uuid_1 is None or uuid_2 is None) and (not excluded or cut_up+cut_down == 0):
                excluded = True
                continue
            if uuid_1 in opponents_ratings:
                if uuid_2 is None:
                    opponents_ratings[uuid_1].append(0)
                else:
                    opponents_ratings[uuid_1].append(id_to_rating_dict[uuid_2])
            if uuid_2 in opponents_ratings:
                if uuid_1 is None:
                    opponents_ratings[uuid_2].append(0)
                else:
                    opponents_ratings[uuid_2].append(id_to_rating_dict[uuid_1])

    opponents_ratings = {
        uuid: cut_list(ratings, cut_up, cut_down) for uuid, ratings in opponents_ratings.items()
    }
    average_ratings = {
        uuid:
            0 if len(opponents_ratings[uuid]) == 0
            else int(sum(opponents_ratings[uuid])/len(opponents_ratings[uuid]))
        for uuid in uuids
    }
    return average_ratings


def get_cumulative_score(uuids, results, score_dict, all_participants, cut_up=0, cut_down=0):
    progressive_scores = {uuid: 0 for uuid in uuids}
    scores = {uuid: 0 for uuid in uuids}

    for i, roun in enumerate(results):
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 in scores:
                scores[uuid_1] += score_dict[score_1]
                if cut_down <= i < len(results)-cut_up:
                    progressive_scores[uuid_1] += scores[uuid_1]
            if uuid_2 in scores:
                scores[uuid_2] += score_dict[score_2]
                if cut_down <= i < len(results)-cut_up:
                    progressive_scores[uuid_2] += scores[uuid_2]
    return shorten_floats(progressive_scores)


def get_direct_encounter(uuids, results, score_dict, all_participants):
    scores = {uuid: 0 for uuid in uuids}

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            if uuid_1 in scores and uuid_2 in scores:
                scores[uuid_1] += score_dict[score_1]-score_dict[score_2]
                scores[uuid_2] += score_dict[score_2]-score_dict[score_1]
    return shorten_floats(scores)


def get_board_points(uuids, results, score_dict_game, results_individual):
    scores = {uuid: 0 for uuid in uuids}
    for roun, roun_individual in zip(results, results_individual):
        for ((uuid_1, _), (uuid_2, _)), result_individual in zip(roun, roun_individual):
            if uuid_1 in scores:
                scores[uuid_1] += sum(score_dict_game[score_1] for (_, score_1), (_, _) in result_individual)
            if uuid_2 in scores:
                scores[uuid_2] += sum(score_dict_game[score_2] for (_, _), (_, score_2) in result_individual)
    return shorten_floats(scores)


def get_berliner_wertung(uuids, results, score_dict_game, results_individual):
    scores = {uuid: 0 for uuid in uuids}
    for roun, roun_individual in zip(results, results_individual):
        for ((uuid_1, _), (uuid_2, _)), result_individual in zip(roun, roun_individual):
            if uuid_1 in scores:
                scores[uuid_1] += sum(
                    score_dict_game[score_1] * (len(result_individual) - i)
                    for i, ((_, score_1), (_, _)) in enumerate(result_individual)
                )
            if uuid_2 in scores:
                scores[uuid_2] += sum(
                    score_dict_game[score_2] * (len(result_individual) - i)
                    for i, ((_, _), (_, score_2)) in enumerate(result_individual)
                )
    return shorten_floats(scores)
