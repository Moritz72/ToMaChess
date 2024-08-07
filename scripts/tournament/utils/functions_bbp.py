from __future__ import annotations
import os
import os.path
from typing import TYPE_CHECKING, Sequence
from subprocess import run
from ..common.pairing_item import Bye, Bye_PA, Pairing_Item
from ..common.pairing import Pairing
from ..common.type_declarations import Participant
from ...common.functions_util import get_app_data_directory, read_file, write_file
from ...common.manager_settings import MANAGER_SETTINGS
from ...player.player import Player
if TYPE_CHECKING:
    from ..tournaments.tournament_swiss import Tournament_Swiss

BBP_Result = tuple[int | None, bool | None, str | None]


def get_color_first_round(tournament: Tournament_Swiss, hash_value: int) -> str:
    match tournament.get_top_seed_color_first_round():
        case "White":
            return "white1"
        case "Black":
            return "black1"
        case _:
            return "white1" if hash_value % 2 else "black1"


def get_bye_score(bye: Pairing_Item, tournament: Tournament_Swiss) -> str:
    assert(isinstance(bye, Bye | Bye_PA))
    if isinstance(bye, Bye):
        return '½' if tournament.get_half_bye() else '-'
    return '+'


def get_bbp_results(tournament: Tournament_Swiss) -> list[list[BBP_Result]]:
    participants = tournament.get_participants()
    results = tournament.get_results()
    item_dict = {participant.get_uuid(): i for i, participant in enumerate(participants)} | {"bye": -1, "": -1}
    bbp_results: list[list[BBP_Result]] = [[(None, None, None) for _ in results] for _ in participants]

    for roun, round_results in enumerate(results):
        for (item_1, score_1), (item_2, score_2) in round_results:
            ind_1, ind_2 = item_dict[item_1], item_dict[item_2]
            if ind_1 >= 0 and ind_2 >= 0:
                bbp_results[ind_1][roun] = (ind_2, True, score_1)
                bbp_results[ind_2][roun] = (ind_1, False, score_2)
            elif ind_1 >= 0:
                bbp_results[ind_1][roun] = (None, None, get_bye_score(item_2, tournament))
            elif ind_2 >= 0:
                bbp_results[ind_2][roun] = (None, None, get_bye_score(item_1, tournament))

    for uuid in tournament.get_drop_outs():
        bbp_results[item_dict[uuid]].append((None, None, '-'))
    for uuid in tournament.get_byes():
        bbp_results[item_dict[uuid]].append((None, None, get_bye_score(Bye(), tournament)))
    return bbp_results


def get_accelerated_count(bbp_results: list[list[BBP_Result]], participants: list[Participant]) -> int:
    limit = (len(participants) + 1) // 2
    limit += limit % 2
    count, i = 0, 0
    while count < limit:
        if (None, None, None) not in bbp_results[i]:
            count += 1
        i += 1
    return count


def convert_side(side: bool) -> str:
    return 'w' if side else 'b'


def convert_points(points: str) -> str:
    return '=' if points == '½' else points


def convert_result(result: BBP_Result) -> str:
    if result[0] is None:
        match result[2]:
            case '+':
                return "  0000 - U"
            case '½':
                return "  0000 - H"
            case _:
                return "  0000 - Z"
    assert(result[1] is not None and result[2] is not None)
    return f"{result[0] + 1} {convert_side(result[1])} {convert_points(result[2])}".rjust(10)


def write_input_file(tournament: Tournament_Swiss) -> None:
    participants = tournament.get_participants()
    score_dict = tournament.get_score_dict()
    standings = tournament.get_standings()
    bbp_results = get_bbp_results(tournament)
    points = [sum([score_dict[points] for _, _, points in result if points is not None]) for result in bbp_results]
    bbp_results_strings = [[convert_result(result) for result in results] for results in bbp_results]
    uuid_to_index_dict = {uuid: i + 1 for i, uuid in enumerate(tournament.get_participant_uuids())}

    lines = f"012 {tournament.get_name()}\r\n"
    for i, (participant, point, results) in enumerate(zip(participants, points, bbp_results_strings)):
        lines += "001 "
        lines += str(i + 1).rjust(4) + " "
        if isinstance(participant, Player):
            lines += (participant.get_sex() or '').lower().rjust(1)
            lines += (participant.get_title() or '').rjust(3) + " "
        else:
            lines += 5 * " "
        lines += participant.get_name()[:33].ljust(33) + " "
        if isinstance(participant, Player):
            lines += str(participant.get_rating() or 0).rjust(4) + " "
            lines += str(participant.get_country() or "")[:3].ljust(3) + " "
        else:
            lines += "   0" + 5 * " "
        lines += 3 * " " + participant.get_uuid()[-8:] + " "
        if isinstance(participant, Player):
            lines += (str(participant.get_birthday()) or '')[-4:].zfill(4) + 7 * " "
        else:
            lines += 11 * " "
        lines += f"{point:.1f}".rjust(4) + " "
        lines += str(standings.participants.index(participant) + 1).rjust(4)
        lines += ''.join(results) + "\r\n"

    if tournament.get_baku_acceleration():
        count = get_accelerated_count(bbp_results, participants)
        full = (tournament.get_rounds() + 1) // 2
        half = full // 2
        full -= half
        full_string, half_string, null_string = (f"{score_dict[res]:.1f}".rjust(5) for res in ('1', '½', '0'))
        points_accelerated = full * [full_string] + half * [half_string]
        points_null = (full + half) * [null_string]
        for i in range(count):
            lines += f"XXA {str(i + 1).rjust(4)}{''.join(points_accelerated)}\r\n"
        for i in range(count, len(participants)):
            lines += f"XXA {str(i + 1).rjust(4)}{''.join(points_null)}\r\n"

    lines += f"XXC {get_color_first_round(tournament, hash(lines))}\r\n"
    lines += f"XXR {tournament.get_rounds()}\r\n"
    lines += f"BBW  {float(score_dict['1'])}\r\n"
    lines += f"BBD  {float(score_dict['½'])}\r\n"
    lines += f"BBL  {float(score_dict['0'])}\r\n"
    lines += f"BBZ  {float(score_dict['-'])}\r\n"
    lines += f"BBF  {float(score_dict['-'])}\r\n"
    lines += f"BBU  {float(score_dict['+'])}\r\n"

    for p_1, p_2 in tournament.get_forbidden_pairings():
        lines += f"XXP {uuid_to_index_dict[p_1]} {uuid_to_index_dict[p_2]}\r\n"

    path = os.path.join(get_app_data_directory(), "temp")
    if not os.path.exists(path):
        os.mkdir(path)
    write_file(os.path.join(path, "bbp_input.txt"), lines)


def process_pairings(pairings_raw: str, participants: Sequence[Participant]) -> list[Pairing]:
    index_dict = {i + 1: participant.get_uuid() for i, participant in enumerate(participants)} | {0: ""}
    return [
        Pairing(index_dict[int(pairing.split(' ')[0])], index_dict[int(pairing.split(' ')[1])])
        for pairing in pairings_raw.split("\r\n")[1:-1]
    ]


def get_pairings_bbp(tournament: Tournament_Swiss) -> list[Pairing] | None:
    bbp_directory: str = MANAGER_SETTINGS["bbp_path"]
    write_input_file(tournament)
    path_bbp = os.path.join(bbp_directory, "bbpPairings.exe")
    path_input = os.path.join(get_app_data_directory(), "temp", "bbp_input.txt")
    path_output = os.path.join(get_app_data_directory(), "temp", "bbp_output.txt")

    try:
        run([path_bbp, "--dutch", path_input, "-p", path_output], check=True, shell=True)
    except:
        return None
    pairings_raw = read_file(path_output)
    return process_pairings(pairings_raw, tournament.get_participants())
