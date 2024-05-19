from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Sequence
from ..common.category_range import Category_Range
from ..common.pairing import Pairing
from ..common.pairing_item import Bye_PA
from ..common.result import Result
from ..common.result_team import Result_Team
from ..common.standings_table import Standings_Table
from ...common.functions_util import has_duplicates, shorten_float
if TYPE_CHECKING:
    from ..tournaments.tournament import Tournament


def get_score_dict_by_point_system(point_system: str, half_bye: bool = False) -> dict[str, float]:
    win_str, draw_str, loss_str = point_system.split(' - ')
    if draw_str == '½':
        draw_str = '.5'
    win, draw, loss = shorten_float(float(win_str)), shorten_float(float(draw_str)), shorten_float(float(loss_str))
    return {'1': win, '½': draw, '0': loss, '+': win, '-': loss, 'b': draw if half_bye else loss}


def reverse_uuid_dict(uuid_dict: dict[str, float]) -> dict[float, list[str]]:
    score_dict: dict[float, list[str]] = {score: [] for score in uuid_dict.values()}
    for uuid, score in uuid_dict.items():
        score_dict[score].append(uuid)
    return score_dict


def get_evaluation_dict(
        current_score: tuple[float, ...], uuids: list[str], function: Callable[[list[str]], dict[str, float]]
) -> dict[tuple[float, ...], list[str]]:
    uuid_dict = function(uuids)
    return {current_score + (score,): uuids for score, uuids in reverse_uuid_dict(uuid_dict).items()}


def get_score_dict_recursive(
        current_score: tuple[float, ...], uuids: list[str], functions: Sequence[Callable[[list[str]], dict[str, float]]]
) -> dict[tuple[float, ...], list[str]]:
    if len(functions) == 0:
        return {current_score: uuids}
    evaluation_dict = get_evaluation_dict(current_score, uuids, functions[0])
    return {
        score_rec: uuids_rec for score, uuids in evaluation_dict.items()
        for score_rec, uuids_rec in get_score_dict_recursive(score, uuids, functions[1:]).items()
    }


def get_standings_with_tiebreaks(tournament: Tournament, category_range: Category_Range | None) -> Standings_Table:
    participants = tournament.get_participants()
    if category_range is not None:
        participants = category_range.filter_list(participants)
    uuid_to_participant_dict = tournament.get_uuid_to_participant_dict()
    uuid_list = [participant.get_uuid() for participant in participants]
    tiebreaks = [tb for tb in tournament.get_tiebreaks() if tb.criteria[0] != "None"]
    headers = ["Name", "Points"] + [tb.criteria[0] for tb in tiebreaks]

    def evaluate_simple(_: list[str]) -> dict[str, float]:
        return {_uuid: _score for _uuid, _score in tournament.get_simple_scores().items() if uuid in uuid_list}

    rank_functions = [evaluate_simple] + [tb.get_evaluation_function(tournament) for tb in tiebreaks]
    score_dict = get_score_dict_recursive(tuple(), uuid_list, rank_functions)

    table_participants = []
    table_scores = []
    for score, uuids in score_dict.items():
        for uuid in uuids:
            table_participants.append(uuid_to_participant_dict[uuid])
            table_scores.append(list(score))
    return Standings_Table(table_participants, table_scores, headers)


def get_team_result(result_team: Result_Team, results_dict: dict[str, float]) -> tuple[str, str]:
    if all(score_1 == '-' and score_2 == '-' for (_, score_1), (_, score_2) in result_team):
        return '-', '-'
    if all(score_1 == '-' for (_, score_1), (_, _) in result_team):
        return '-', '+'
    if all(score_2 == '-' for (_, _), (_, score_2) in result_team):
        return '+', '-'
    sum_1 = sum(results_dict[score_1] for (_, score_1), (_, _) in result_team)
    sum_2 = sum(results_dict[score_2] for (_, _), (_, score_2) in result_team)
    if sum_1 > sum_2:
        return '1', '0'
    if sum_2 > sum_1:
        return '0', '1'
    return '½', '½'


def is_valid_lineup(pairings: Sequence[Pairing], uuids: Sequence[str], side: int, enforce_lineup: bool) -> bool:
    if not enforce_lineup:
        return not has_duplicates([pairing[side] for pairing in pairings])
    index: int | None = 0
    for pairing in pairings:
        item = pairing[side]
        if isinstance(item, list):
            return False
        if item.is_bye():
            index = None
            continue
        number = uuids.index(item) + 1
        if index is None or number <= index:
            return False
        index = number
    return True


def get_score_dict_keizer(
        uuids: Sequence[str], score_dict: dict[str, float], results: list[list[Result]], p_max: int, bye_percentage: int
) -> dict[str, float]:
    if len(results) == 0:
        return {uuid: float(p_max - i) for i, uuid in enumerate(uuids)}
    scores = get_score_dict_keizer(uuids, score_dict, results[:-1], p_max, bye_percentage)
    uuid_to_index = {uuid: list(scores).index(uuid) for uuid in scores}
    scores = {uuid: p_max - i for i, uuid in enumerate(uuids)}

    for result_list in results:
        for (item_1, score_1), (item_2, score_2) in result_list:
            if item_1 not in uuids:
                factor = 1 if isinstance(item_1, Bye_PA) else bye_percentage / 100
                scores[item_2] += score_dict['+'] * (p_max - uuid_to_index[item_2]) * factor
            elif item_2 not in uuids:
                factor = 1 if isinstance(item_2, Bye_PA) else bye_percentage / 100
                scores[item_1] += score_dict['+'] * (p_max - uuid_to_index[item_1]) * factor
            else:
                scores[item_1] += score_dict[score_1] * (p_max - uuid_to_index[item_2])
                scores[item_2] += score_dict[score_2] * (p_max - uuid_to_index[item_1])

    uuids = sorted(list(scores), key=lambda x: scores[x], reverse=True)
    return {uuid: scores[uuid] for uuid in uuids}
