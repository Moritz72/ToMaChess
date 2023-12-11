from __future__ import annotations
from typing import TYPE_CHECKING, Sequence, cast
from .result import Result
from .player import Player
from .variable_results import Variable_Results
from .functions_util import shorten_float
if TYPE_CHECKING:
    from .tournament import Tournament

Result_List = list[tuple[str | None, str, int]]
UUID_To_Result_List_Dict = dict[str, Result_List]
Score_Dict = dict[str, float]


def shorten_floats(scores: Score_Dict) -> Score_Dict:
    return {uuid: shorten_float(score) for uuid, score in scores.items()}


def cut_list(lis: Sequence[float], cut_up: int, cut_down: int) -> Sequence[float]:
    while cut_up + cut_down > len(lis):
        if cut_up >= cut_down:
            cut_up -= 1
        else:
            cut_down -= 1
    if cut_up:
        return lis[cut_down:-cut_up]
    return lis[cut_down:]


def add_result_list_to_uuid_dict(result: Result, uuid_dict: UUID_To_Result_List_Dict, roun: int) -> None:
    for i in range(2):
        uuid = result[i][0]
        if uuid is None:
            continue
        elif uuid not in uuid_dict:
            uuid_dict[uuid] = []
        uuid_dict[uuid].append((result[1 - i][0], result[i][1], roun))


def get_uuid_to_result_list_dict(results: Variable_Results) -> UUID_To_Result_List_Dict:
    uuid_to_results_dict: UUID_To_Result_List_Dict = dict()
    for roun, round_results in enumerate(results):
        for result in round_results:
            add_result_list_to_uuid_dict(result, uuid_to_results_dict, roun)
    return uuid_to_results_dict


def score_from_result_list(result_list: Result_List, score_dict: Score_Dict, half_bye: bool = False) -> float:
    return sum(score_dict['½'] if res == '+' and half_bye else score_dict[res] for _, res, _ in result_list)


def get_scores_from_uuid_dict(
        uuid_dict: UUID_To_Result_List_Dict, score_dict: Score_Dict, half_bye: bool = False
) -> Score_Dict:
    return {uuid: score_from_result_list(result_list, score_dict, half_bye) for uuid, result_list in uuid_dict.items()}


def get_opp_score(
        opp: str | None, roun: int, score_dict: Score_Dict, res_list: Result_List, tournament: Tournament, virtual: bool
) -> float:
    score_dict_tournament = tournament.get_score_dict()
    if opp is not None:
        return score_dict[opp]
    score = score_from_result_list(res_list[:roun], score_dict_tournament)
    if virtual:
        return score + (tournament.get_round() - roun - 1) * score_dict_tournament['½']
    return score + score_dict_tournament['-']


def get_buchholz(
        uuids: Sequence[str], tournament: Tournament, cut_up: int = 0, cut_down: int = 0, virtual: bool = False
) -> Score_Dict:
    uuid_dict = get_uuid_to_result_list_dict(tournament.get_results())
    score_dict = get_scores_from_uuid_dict(uuid_dict, tournament.get_score_dict())

    tb_dict = {
        uuid: [
            get_opp_score(opp, roun, score_dict, uuid_dict[uuid], tournament, virtual)
            for opp, _, roun in uuid_dict[uuid]
        ] if uuid in uuid_dict else [] for uuid in uuids
    }

    return shorten_floats({uuid: sum(cut_list(sorted(scores), cut_up, cut_down)) for uuid, scores in tb_dict.items()})


def get_buchholz_sum(
        uuids: Sequence[str], tournament: Tournament, cut_up: int = 0, cut_down: int = 0, virtual: bool = False
) -> Score_Dict:
    buchholz_dict = get_buchholz(list(tournament.get_uuid_to_participant_dict()), tournament, cut_up, cut_down, virtual)
    uuid_dict = get_uuid_to_result_list_dict(tournament.get_results())

    return shorten_floats({
        uuid: sum(0 if opp is None else buchholz_dict[opp] for opp, _, _ in uuid_dict[uuid]) if uuid in uuid_dict
        else 0 for uuid in uuids
    })


def get_sonneborn_berger(
        uuids: Sequence[str], tournament: Tournament, cut_up: int = 0, cut_down: int = 0, virtual: bool = False
) -> Score_Dict:
    score_dict_tournament = tournament.get_score_dict()
    uuid_dict = get_uuid_to_result_list_dict(tournament.get_results())
    score_dict = get_scores_from_uuid_dict(uuid_dict, tournament.get_score_dict())

    tb_dict = {
        uuid: [
            score_dict_tournament[res] * get_opp_score(opp, roun, score_dict, uuid_dict[uuid], tournament, virtual)
            for opp, res, roun in uuid_dict[uuid]
        ] if uuid in uuid_dict else [] for uuid in uuids
    }

    return shorten_floats({uuid: sum(cut_list(sorted(scores), cut_up, cut_down)) for uuid, scores in tb_dict.items()})


def get_blacks(uuids: Sequence[str], tournament: Tournament) -> Score_Dict:
    blacks = {uuid: 0. for uuid in uuids}

    for round_results in tournament.get_results():
        for (uuid_1, _), (uuid_2, _) in round_results:
            if uuid_1 is None or uuid_2 is None or uuid_2 not in blacks:
                continue
            blacks[uuid_2] += 1

    return shorten_floats(blacks)


def get_number_of_wins(uuids: Sequence[str], tournament: Tournament, include_forfeits: bool = False) -> Score_Dict:
    wins = {uuid: 0. for uuid in uuids}

    for round_results in tournament.get_results():
        for (uuid_1, score_1), (uuid_2, score_2) in round_results:
            if uuid_1 in wins and (score_1 == '1' or (include_forfeits and score_1 == '+')):
                wins[uuid_1] += 1
            if uuid_2 in wins and (score_2 == '1' or (include_forfeits and score_2 == '+')):
                wins[uuid_2] += 1

    return shorten_floats(wins)


def get_number_of_black_wins(
        uuids: Sequence[str], tournament: Tournament, include_forfeits: bool = False
) -> Score_Dict:
    black_wins = {uuid: 0. for uuid in uuids}

    for round_results in tournament.get_results():
        for (uuid_1, score_1), (uuid_2, score_2) in round_results:
            if uuid_1 is None or uuid_2 is None or uuid_2 not in black_wins:
                continue
            if score_2 == '1' or (score_2 == '+' and include_forfeits):
                black_wins[uuid_2] += 1

    return shorten_floats(black_wins)


def get_opponent_average_rating(
        uuids: Sequence[str], tournament: Tournament, cut_up: int = 0, cut_down: int = 0, include_forfeits: bool = False
) -> Score_Dict:
    participants = cast(list[Player], tournament.get_participants())
    rating_dict = {participant.get_uuid(): participant.get_rating() for participant in participants}
    uuid_dict = get_uuid_to_result_list_dict(tournament.get_results())

    tb_dict = cast(dict[str, list[float]], {
        uuid: [
            rating_dict[opp] for opp, res, _ in uuid_dict[uuid]
            if opp is not None and (res in ('1', '½', '0') or include_forfeits)
        ] if uuid in uuid_dict else [] for uuid in uuids
    })

    return shorten_floats({
        uuid: sum(cut_list(sorted(scores), cut_up, cut_down)) // max(1, len(cut_list(sorted(scores), cut_up, cut_down)))
        for uuid, scores in tb_dict.items()
    })


def get_progressive_score(
        uuids: Sequence[str], tournament: Tournament, cut_up: int = 0, cut_down: int = 0
) -> Score_Dict:
    tb_dict: dict[str, list[float]] = {uuid: [] for uuid in uuids}
    uuid_dict = get_uuid_to_result_list_dict(tournament.get_results())

    for uuid in uuids:
        if uuid not in uuid_dict:
            continue
        r, i = 0, 0
        while i < len(uuid_dict[uuid]) and r < tournament.get_round() - 1:
            _, res, roun = uuid_dict[uuid][i]
            current = 0 if i == 0 else tb_dict[uuid][-1]
            add = tournament.get_score_dict()[res] if roun == r else 0
            tb_dict[uuid].append(current + add)
            if roun == r:
                i += 1
            r += 1

    return shorten_floats({uuid: sum(cut_list(sorted(scores), cut_up, cut_down)) for uuid, scores in tb_dict.items()})


def get_direct_encounter(uuids: Sequence[str], tournament: Tournament) -> Score_Dict:
    scores = {uuid: 0. for uuid in uuids}
    score_dict = tournament.get_score_dict()

    for round_results in tournament.get_results():
        for (uuid_1, score_1), (uuid_2, score_2) in round_results:
            if uuid_1 in scores and uuid_2 in scores:
                scores[uuid_1] += score_dict[score_1] - score_dict[score_2]
                scores[uuid_2] += score_dict[score_2] - score_dict[score_1]

    return shorten_floats(scores)


def get_board_points(uuids: Sequence[str], tournament: Tournament) -> Score_Dict:
    scores = {uuid: 0. for uuid in uuids}
    score_dict_game = tournament.get_score_dict_game()

    for round_results, round_results_team in zip(tournament.get_results(), tournament.get_results_team()):
        for ((uuid_1, _), (uuid_2, _)), result_team in zip(round_results, round_results_team):
            if uuid_1 in scores:
                scores[uuid_1] += sum(score_dict_game[score_1] for (_, score_1), (_, _) in result_team)
            if uuid_2 in scores:
                scores[uuid_2] += sum(score_dict_game[score_2] for (_, _), (_, score_2) in result_team)

    return shorten_floats(scores)


def get_berliner_wertung(uuids: Sequence[str], tournament: Tournament) -> dict[str, float]:
    scores = {uuid: 0. for uuid in uuids}
    score_dict_game = tournament.get_score_dict_game()
    boards = tournament.get_boards()

    for round_results, round_results_team in zip(tournament.get_results(), tournament.get_results_team()):
        for ((uuid_1, _), (uuid_2, _)), result_team in zip(round_results, round_results_team):
            if uuid_1 in scores:
                scores[uuid_1] += sum(
                    score_dict_game[score_1] * (boards - i) for i, ((_, score_1), (_, _)) in enumerate(result_team)
                )
            if uuid_2 in scores:
                scores[uuid_2] += sum(
                    score_dict_game[score_2] * (boards - i) for i, ((_, _), (_, score_2)) in enumerate(result_team)
                )

    return shorten_floats(scores)
