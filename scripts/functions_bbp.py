import os
import os.path
from typing import Sequence, cast
from subprocess import run
from .manager_settings import MANAGER_SETTINGS
from .pairing import Pairing
from .result import Result
from .tournament import Participant
from .player import Player
from .functions_util import read_file, write_file, get_app_data_directory

BBP_Result = tuple[int | None, bool | None, str | None]


def get_uuid_to_index_dict(participants: Sequence[Participant]) -> dict[str | None, int | None]:
    return {None: None} | {participant.get_uuid(): i for i, participant in enumerate(participants)}


def get_index_to_uuid_dict(participants: Sequence[Participant]) -> dict[int, str | None]:
    return {0: None} | {i + 1: participant.get_uuid() for i, participant in enumerate(participants)}


def get_data_from_results(
        participants: Sequence[Participant], results: Sequence[Sequence[Result]], drop_outs: Sequence[str]
) -> tuple[list[int | None], list[list[BBP_Result]]]:
    uuid_dict = get_uuid_to_index_dict(participants)
    ratings: list[int | None] = [
        participant.get_rating() if isinstance(participant, Player) else None for participant in participants
    ]
    bbp_results: list[list[BBP_Result]] = [[(None, None, None) for _ in results] for _ in participants]

    for roun, round_results in enumerate(results):
        for (uuid_1, score_1), (uuid_2, score_2) in round_results:
            ind_1, ind_2 = uuid_dict[uuid_1], uuid_dict[uuid_2]
            if uuid_1 is not None and ind_1 is not None:
                bbp_results[ind_1][roun] = (ind_2, True, score_1)
            if uuid_2 is not None and ind_2 is not None:
                bbp_results[ind_2][roun] = (ind_1, False, score_2)
    for uuid in drop_outs:
        bbp_results[cast(int, uuid_dict[uuid])].append((None, None, None))
    return ratings, bbp_results


def convert_side(side: bool) -> str:
    return 'w' if side else 'b'


def convert_points(points: str) -> str:
    return '=' if points == '½' else points


def convert_result(result: BBP_Result) -> str:
    if result[2] is None:
        return "  0000 - Z"
    if result[0] is None:
        return "  0000 - U"
    return f"{result[0] + 1} {convert_side(cast(bool, result[1]))} {convert_points(result[2])}".rjust(10)


def write_input_file(
        ratings: Sequence[int | None], bbp_results: Sequence[Sequence[BBP_Result]],
        rounds: int, score_dict: dict[str, float]
) -> None:
    points = [sum([score_dict[points] for _, _, points in result if points is not None]) for result in bbp_results]
    bbp_results_strings = [[convert_result(result) for result in results] for results in bbp_results]
    temp = sorted(((i + 1, points) for i, points in enumerate(points)), key=lambda x: x[1], reverse=True)
    ranks = [rank for rank, _ in temp]

    lines = "012 AutoTest Tournament 1110065304\r\n"
    for i, (rating, point, rank, results) in enumerate(zip(ratings, points, ranks, bbp_results_strings)):
        lines += (
            f"001{str(i + 1).rjust(5)}      Test{str(i + 1).zfill(4)} Player{str(i + 1).zfill(4)}"
            f"{str(rating or '').rjust(19)}{str(point).rjust(32)}{str(rank).rjust(5)}{''.join(results)}\r\n"
        )
    lines += f"XXR {rounds}\r\n"
    lines += f"BBW  {float(score_dict['1'])}\r\n"
    lines += f"BBD  {float(score_dict['½'])}\r\n"
    lines += f"BBL  {float(score_dict['0'])}\r\n"
    lines += f"BBF  {float(score_dict['-'])}\r\n"
    lines += f"BBU  {float(score_dict['+'])}\r\n"

    path = os.path.join(get_app_data_directory(), "temp")
    if not os.path.exists(path):
        os.mkdir(path)
    write_file(os.path.join(path, "bbp_input.txt"), lines)


def process_pairings(pairings_raw: str, participants: Sequence[Participant]) -> list[Pairing]:
    index_dict = get_index_to_uuid_dict(participants)
    return [
        Pairing(index_dict[int(pairing.split(' ')[0])], index_dict[int(pairing.split(' ')[1])])
        for pairing in pairings_raw.split("\r\n")[1:-1]
    ]


def get_pairings_bbp(
        participants: Sequence[Participant], results: Sequence[Sequence[Result]],
        rounds: int, score_dict: dict[str, float], drop_outs: Sequence[str]
) -> list[Pairing]:
    bbp_directory: str = MANAGER_SETTINGS["bbp_path"]
    ratings, bbp_results = get_data_from_results(participants, results, drop_outs)
    write_input_file(ratings, bbp_results, rounds, score_dict)
    path_bbp = os.path.join(bbp_directory, "bbpPairings.exe")
    path_input = os.path.join(get_app_data_directory(), "temp", "bbp_input.txt")
    path_output = os.path.join(get_app_data_directory(), "temp", "bbp_output.txt")

    try:
        run([path_bbp, "--dutch", path_input, "-p", path_output], check=True, shell=True)
    except:
        return NotImplemented
    pairings_raw = read_file(path_output)
    return process_pairings(pairings_raw, participants)
