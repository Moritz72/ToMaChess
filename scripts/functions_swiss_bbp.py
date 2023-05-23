from subprocess import run
from .functions_settings import get_settings
from .functions_util import read_file, write_file


def get_data_from_player_results(players, results):
    uuid_to_index_dict = {None: -1} | {player.get_uuid(): i for i, player in enumerate(players)}
    player_ratings = [player.get_rating() for player in players]
    player_results = [[] for player in players]

    for roun in results:
        for (uuid_1, score_1), (uuid_2, score_2) in roun:
            ind_1 = uuid_to_index_dict[uuid_1]
            ind_2 = uuid_to_index_dict[uuid_2]
            if uuid_1 is not None:
                player_results[ind_1].append((ind_2, True, score_1))
            if uuid_2 is not None:
                player_results[ind_2].append((ind_1, False, score_2))
    return player_ratings, player_results


def convert_side(side):
    return 'w' if side else 'b'


def convert_points(points):
    return '=' if points == '½' else points


def write_input_file(player_ratings, player_results, rounds, score_dict, bbp_directory):
    player_points = [sum([score_dict[points] for _, _, points in result]) for result in player_results]
    player_results = [
        [
            f"{opponent+1} {convert_side(side)} {convert_points(points)}".rjust(10)
            for opponent, side, points in results
        ] for results in player_results
    ]
    player_ranks = sorted(((i + 1, points) for i, points in enumerate(player_points)), key=lambda x: x[1], reverse=True)
    player_ranks = [rank for rank, _ in player_ranks]

    lines = "012 AutoTest Tournament 1110065304\r\n"
    for i, (rating, points, rank, results) in \
            enumerate(zip(player_ratings, player_points, player_ranks, player_results)):
        lines = lines + (
            f"001{str(i + 1).rjust(5)}      Test{str(i + 1).zfill(4)} Player{str(i + 1).zfill(4)}"
            f"{str(rating).rjust(19)}{str(points).rjust(32)}{str(rank).rjust(5)}{''.join(results)}\r\n"
        )
    lines = lines + f"XXR {rounds}\r\n"
    if not player_results[0]:
        lines = lines + "XXC white1\r\n"
    lines = lines + f"BBW  {float(score_dict['1'])}\r\n"
    lines = lines + f"BBD  {float(score_dict['½'])}\r\n"
    lines = lines + f"BBL  {float(score_dict['0'])}\r\n"
    lines = lines + f"BBF  {float(score_dict['-'])}\r\n"
    lines = lines + f"BBU  {float(score_dict['+'])}\r\n"

    write_file(f"{bbp_directory}/input.txt", lines)


def process_pairings(pairings_raw, players):
    index_to_uuid_dict = {0: None} | {i + 1: player.get_uuid() for i, player in enumerate(players)}
    pairings = [
        tuple(index_to_uuid_dict[int(ind)] for ind in pairing.split(' '))
        for pairing in pairings_raw.split("\r\n")[1:-1]
    ]
    return pairings


def get_pairings_bbp(players, results, rounds, score_dict):
    bbp_directory = get_settings()["bbp_path"]
    player_ratings, player_results = get_data_from_player_results(players, results)
    write_input_file(player_ratings, player_results, rounds, score_dict, bbp_directory)
    command = [
        f"{bbp_directory}/bbpPairings.exe", "--dutch", f"{bbp_directory}/input.txt", "-p", f"{bbp_directory}/output.txt"
    ]
    run(command, check=True)
    pairings_raw = read_file(f"{bbp_directory}/output.txt")
    pairings = process_pairings(pairings_raw, players)
    return pairings
