import os
import os.path
from subprocess import run
from .class_settings_handler import SETTINGS_HANDLER
from .functions_util import read_file, write_file, get_app_data_directory


def get_data_from_player_results(players, results, drop_outs):
    uuid_to_index_dict = {None: -1} | {player.get_uuid(): i for i, player in enumerate(players)}
    player_ratings = [player.get_rating() for player in players]
    player_results = [[] for player in players]

    for roun in results:
        uuids = {player.get_uuid() for player in players}
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            ind_1, ind_2 = uuid_to_index_dict[uuid_1], uuid_to_index_dict[uuid_2]
            if uuid_1 is not None:
                player_results[ind_1].append((ind_2, True, score_1))
                uuids.discard(uuid_1)
            if uuid_2 is not None:
                player_results[ind_2].append((ind_1, False, score_2))
                uuids.discard(uuid_2)
        for uuid in uuids:
            player_results[uuid_to_index_dict[uuid]].append((None, None, None))
    for uuid in drop_outs:
        player_results[uuid_to_index_dict[uuid]].append((None, None, None))
    return player_ratings, player_results


def convert_side(side):
    return 'w' if side else 'b'


def convert_points(points):
    return '=' if points == '½' else points


def convert_result(result):
    if result[0] is None:
        return "  0000 - Z"
    return f"{result[0]+1} {convert_side(result[1])} {convert_points(result[2])}".rjust(10)


def write_input_file(player_ratings, player_results, rounds, score_dict, bbp_directory):
    player_points = [
        sum([score_dict[points] for _, _, points in result if points is not None]) for result in player_results
    ]
    player_results = [[convert_result(result) for result in results] for results in player_results]
    player_ranks = sorted(((i + 1, points) for i, points in enumerate(player_points)), key=lambda x: x[1], reverse=True)
    player_ranks = [rank for rank, _ in player_ranks]

    lines = "012 AutoTest Tournament 1110065304\r\n"
    for i, (rating, points, rank, results) in \
            enumerate(zip(player_ratings, player_points, player_ranks, player_results)):
        lines += (
            f"001{str(i + 1).rjust(5)}      Test{str(i + 1).zfill(4)} Player{str(i + 1).zfill(4)}"
            f"{str(rating).rjust(19)}{str(points).rjust(32)}{str(rank).rjust(5)}{''.join(results)}\r\n"
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


def process_pairings(pairings_raw, players):
    index_to_uuid_dict = {0: None} | {i + 1: player.get_uuid() for i, player in enumerate(players)}
    return [
        tuple(index_to_uuid_dict[int(ind)] for ind in pairing.split(' '))
        for pairing in pairings_raw.split("\r\n")[1:-1]
    ]


def get_pairings_bbp(players, results, rounds, score_dict, drop_outs):
    bbp_directory = SETTINGS_HANDLER.get("bbp_path")
    player_ratings, player_results = get_data_from_player_results(players, results, drop_outs)
    write_input_file(player_ratings, player_results, rounds, score_dict, bbp_directory)
    path_bbp = os.path.join(bbp_directory, "bbpPairings.exe")
    path_input = os.path.join(get_app_data_directory(), "temp", "bbp_input.txt")
    path_output = os.path.join(get_app_data_directory(), "temp", "bbp_output.txt")

    try:
        run([path_bbp, "--dutch", path_input, "-p", path_output], check=True, shell=True)
    except:
        return
    pairings_raw = read_file(path_output)
    return process_pairings(pairings_raw, players)
