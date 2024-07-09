from typing import Sequence, cast
from .functions_pairing import PAIRING_FUNCTIONS
from ..common.bracket_tree import Bracket_Tree, Bracket_Tree_Node
from ..common.pairing_item import Bye_PA, Pairing_Item, get_item_from_string
from ..common.result import Result
from ..parameters.parameter_armageddon import Parameter_Armageddon
from ..variables.variable_knockout_standings import Variable_Knockout_Standings
from ..variables.variable_pairings import Variable_Pairings
from ..variables.variable_results import Variable_Results

Results_Dict = dict[tuple[Pairing_Item, Pairing_Item], list[tuple[str, str]]]


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


def get_layer_results_dict(results: list[list[Result]], auto_advance: list[str]) -> Results_Dict:
    results_dict: Results_Dict = dict()
    for advancer in auto_advance:
        results_dict[(get_item_from_string(advancer), Bye_PA())] = []
    for round_results in results:
        for result in round_results:
            pair = (result[0][0], result[1][0])
            score = (result[0][1], result[1][1])
            if pair in results_dict:
                results_dict[pair].append(score)
            elif pair[::-1] in results_dict:
                results_dict[pair[::-1]].append(score[::-1])
            else:
                results_dict[pair] = [score]
    return results_dict


def get_layers(
        standings_dict: Variable_Knockout_Standings, pairings: Variable_Pairings, results: Variable_Results,
        history: list[list[str]], ends: list[int]
) -> list[list[Bracket_Tree_Node]]:
    levels = {uuid: standing.level for uuid, standing in standings_dict.items()} | {"": -1}
    results_dicts = [get_layer_results_dict(results[ends[i]:ends[i + 1]], history[i]) for i in range(len(history))]
    layers = [[
        Bracket_Tree_Node(
            (item_1, item_2), scores, None if levels[item_1] == levels[item_2] else levels[item_1] < levels[item_2]
        )
        for (item_1, item_2), scores in results_dict.items()
    ] for results_dict in results_dicts]

    if bool(pairings) and all(pairing.is_fixed() for pairing in pairings) and len(results) in ends:
        pairs = [(cast(Pairing_Item, item_1), cast(Pairing_Item, item_2)) for item_1, item_2 in pairings]
        pairs_flat = [item for pair in pairs for item in pair]
        advancers = [get_item_from_string(uuid) for uuid in standings_dict.get_uuids() if uuid not in pairs_flat]
        layers.append(
            [Bracket_Tree_Node((advancer, Bye_PA()), [], False) for advancer in advancers] +
            [Bracket_Tree_Node(pair, []) for pair in pairs]
        )

    i = 1
    while i < len(layers):
        if len(layers[-i - 1]) > 2 * len(layers[-i]):
            items = [cast(Pairing_Item, item) for node in layers[-i] for item in node.items]
            nodes = [Bracket_Tree_Node((item, Bye_PA()), [], None if item.is_bye() else False) for item in items]
            layers.insert(-i, nodes)
        i += 1
    return layers


def connect_layers(layer_1: list[Bracket_Tree_Node], layer_2: list[Bracket_Tree_Node]) -> None:
    nodes_to_connect = layer_1.copy()
    for parent_node in layer_2:
        children = [node for node in layer_1 if bool((set(node.items) & set(parent_node.items)) - {Bye_PA()})]
        parent_node.set_children(children, len(children) * [True])
        if len(children) == 1:
            if parent_node.items[0] != children[0].items[0] and parent_node.items[1] != children[0].items[1]:
                parent_node.swap()
        elif len(children) == 2:
            if parent_node.items[0] not in children[0].items:
                parent_node.swap()
        nodes_to_connect = [node for node in nodes_to_connect if node not in children]
    for _ in range(2):
        j = 1
        while bool(nodes_to_connect) and j <= len(layer_2):
            parent_node = layer_2[-j]
            if parent_node.get_n_children() < 2:
                parent_node.set_children([nodes_to_connect[-1]], [False])
                nodes_to_connect.pop()
            j += 1


def add_future_layer(layers: list[list[Bracket_Tree_Node]], pairing_method: str | None) -> None:
    pairs = PAIRING_FUNCTIONS[pairing_method or "Fold"](len(layers[-1]), True)
    layers.append([Bracket_Tree_Node((None, None), []) for _ in range(len(pairs))])
    for node, (p_1, p_2) in zip(layers[-1], pairs):
        node.set_children([layers[-2][p_1], layers[-2][p_2]], 2 * [pairing_method is not None])


def get_bracket_tree(
        standings_dict: Variable_Knockout_Standings, pairings: Variable_Pairings, results: Variable_Results,
        auto_advance_history: list[list[str]], pairing_method: str, end_rounds: list[int]
) -> Bracket_Tree:
    end_rounds = [0] + end_rounds
    for i in range(1, len(end_rounds)):
        end_rounds[i] += end_rounds[i - 1]
    layers = get_layers(standings_dict, pairings, results, auto_advance_history, end_rounds)
    for i in range(1, len(layers)):
        connect_layers(layers[i - 1], layers[i])
    if not bool(layers):
        return Bracket_Tree(("Bracket Tree",), Bracket_Tree_Node((Bye_PA(), Bye_PA()), []))
    while len(layers[-1]) > 1:
        add_future_layer(layers, pairing_method if pairing_method in ("Fold", "Slide") else None)
    return Bracket_Tree(("Bracket Tree",), layers[-1][0])
