from random import shuffle
from typing import Any, Sequence, cast
from .tournament import Tournament
from ..common.bracket_tree import Bracket_Tree
from ..common.category_range import Category_Range
from ..common.cross_table import Cross_Table
from ..common.pairing import Pairing
from ..common.result import Result
from ..common.result_team import Result_Team
from ..common.standings_table import Standings_Table
from ..common.type_declarations import Participant
from ..parameters.parameter_armageddon import Parameter_Armageddon
from ..registries.tournament_registry import TEAM_TOURNAMENT_REGISTRY, TOURNAMENT_REGISTRY
from ..variables.variable_knockout_standings import Variable_Knockout_Standings
from ..utils.functions_pairing import PAIRING_FUNCTIONS
from ..utils.functions_tournament_knockout import get_bracket_tree, get_end_rounds, reverse_participant_standings, \
    update_participant_standings
from ...common.functions_util import has_duplicates
from ...database.db_player import sort_players_swiss
from ...player.player import Player


def get_scores(score_1: str, score_2: str, score_dict: dict[str, float]) -> tuple[list[float], list[float]]:
    if score_1 == '-' == score_2:
        return [.5], [.5]
    else:
        return [score_dict[score_1]], [score_dict[score_2]]


@TOURNAMENT_REGISTRY.register("Knockout")
class Tournament_Knockout(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Knockout"
        self.parameters = {
            "games": 2,
            "games_per_tiebreak": 2,
            "pairing_method": ["Fold", "Slide", "Adjacent", "Random", "Custom"],
            "armageddon": Parameter_Armageddon()
        } | self.parameters
        self.variables = {
            "standings_dict": Variable_Knockout_Standings(dict()),
            "auto_advance_history": []
        } | self.variables
        self.parameters_display = {
            "games": "Games per Match",
            "games_per_tiebreak": "Games per Tiebreak",
            "pairing_method": "Pairing Method",
            "armageddon": "Armageddon"
        }

    def get_changeable_parameters(self, initial: bool = False) -> dict[str, Any]:
        if initial:
            return super().get_changeable_parameters(initial)
        return dict()

    def get_round_name(self, r: int) -> tuple[str, ...]:
        games = self.get_games()
        games_per_tiebreak = self.get_games_per_tiebreak()
        armageddon = self.get_armageddon()
        standings_dict = self.get_standings_dict()
        end_rounds = get_end_rounds(standings_dict, games, games_per_tiebreak, armageddon, *self.get_totals())

        counter = 1
        while len(end_rounds) > 0 and r > end_rounds[0]:
            r -= end_rounds.pop(0)
            counter += 1

        if armageddon.is_armageddon(games, games_per_tiebreak, r):
            return "Round", ' ', f"{counter}.A"
        if r <= games:
            if games == 1:
                return "Round", ' ', f"{counter}"
            return "Round", ' ', f"{counter}.{r}"
        return "Round", ' ', f"{counter}.T{r - games}"

    def get_standings(self, category_range: Category_Range | None = None) -> Standings_Table:
        headers = ["Name", "Matches", "Match Points"]
        if self.is_team_tournament():
            headers.extend(["Board Points", "Berlin Rating"])
        participants = self.get_participants()
        standings_dict = self.get_standings_dict()
        if category_range is not None:
            participants = category_range.filter_list(participants)

        uuids = [participant.get_uuid() for participant in participants]
        entries = [[standings_dict[uuid].level, *standings_dict[uuid].score] for uuid in uuids]
        if self.is_team_tournament():
            for entry in entries:
                entry[1] *= 2

        return Standings_Table(participants, entries, headers)

    def get_games(self) -> int:
        return cast(int, self.get_parameter("games"))

    def get_games_per_tiebreak(self) -> int:
        return cast(int, self.get_parameter("games_per_tiebreak"))

    def get_pairing_method(self) -> str:
        return cast(str, self.get_parameter("pairing_method")[0])

    def get_armageddon(self) -> Parameter_Armageddon:
        return cast(Parameter_Armageddon, self.get_parameter("armageddon"))

    def get_standings_dict(self) -> Variable_Knockout_Standings:
        return cast(Variable_Knockout_Standings, self.get_variable("standings_dict"))

    def get_auto_advance_history(self) -> list[list[str]]:
        return cast(list[list[str]], self.get_variable("auto_advance_history"))

    @staticmethod
    def get_initial_score() -> list[float]:
        return [0.]

    def get_totals(self) -> tuple[list[float], list[float]]:
        return [self.get_games()], [self.get_games_per_tiebreak()]

    def get_latest_scores(self) -> list[tuple[list[float], list[float]]]:
        return [
            get_scores(score_1, score_2, self.get_score_dict()) for (_, score_1), (_, score_2) in self.get_results()[-1]
        ]

    def get_cross_table(self, i: int) -> Cross_Table:
        return NotImplemented

    def get_cross_tables(self) -> int:
        return 0

    def get_bracket_tree(self, i: int) -> Bracket_Tree:
        assert(i < self.get_bracket_trees())
        standings_dict = self.get_standings_dict()
        end_rounds = get_end_rounds(
            standings_dict, self.get_games(), self.get_games_per_tiebreak(), self.get_armageddon(), *self.get_totals()
        )
        return get_bracket_tree(
            self.get_standings_dict(), self.get_pairings(), self.get_results(),
            self.get_auto_advance_history(), self.get_pairing_method(), end_rounds
        )

    def get_bracket_trees(self) -> int:
        return 1

    def set_participants(self, participants: Sequence[Participant], from_order: bool = False) -> None:
        super().set_participants(participants, from_order=from_order)
        uuids = self.get_participant_uuids()
        standings_dict = self.get_standings_dict()
        current_level = standings_dict.get_current_level()
        for uuid in uuids:
            if uuid not in standings_dict:
                standings_dict.add(uuid, current_level, self.get_initial_score())

    def is_valid_parameters(self) -> bool:
        return self.get_games() > 0 and self.get_games_per_tiebreak() > 0

    def is_valid_pairings(self, pairings: Sequence[Pairing]) -> bool:
        assert(all(pairing.is_fixed() for pairing in pairings))
        return not has_duplicates([item for item, _ in pairings] + [item for _, item in pairings])

    def is_done(self) -> bool:
        return tuple(standing.beaten_by_seed for standing in self.get_standings_dict().values()).count(None) == 1

    def is_drop_in_allowed(self) -> bool:
        standings_dict = self.get_standings_dict()
        return all(standings_dict[uuid].score == self.get_initial_score() for uuid in standings_dict.get_uuids())

    def is_add_byes_allowed(self) -> bool:
        return False

    def is_seeding_allowed(self) -> bool:
        return self.get_round() == 1

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        super().add_results(results)
        games = self.get_games()
        games_per_tiebreak = self.get_games_per_tiebreak()
        armageddon = self.get_armageddon()
        standings_dict = self.get_standings_dict()
        first_round = all(standings_dict[uuid].score == self.get_initial_score() for uuid in standings_dict.get_uuids())
        level = standings_dict[cast(str, self.get_results()[-1][0][0][0])].level
        uuids = set()

        for ((item_1, _), (item_2, _)), (score_1, score_2) in zip(self.get_results()[-1], self.get_latest_scores()):
            update_participant_standings(
                item_1, item_2, score_1, score_2, standings_dict,
                games, games_per_tiebreak, armageddon, *self.get_totals()
            )
            uuids |= {item_1, item_2}

        if first_round:
            alives_difference = set(standings_dict.get_alives()).difference(uuids)
            for uuid in alives_difference:
                standings_dict[uuid].level = level + 1
            self.get_auto_advance_history().append(sorted(alives_difference, key=lambda x: standings_dict[x].seed))
        self.set_participants(sorted(self.get_participants(), key=lambda x: standings_dict[x.get_uuid()].seed))

    def remove_results(self) -> None:
        games = self.get_games()
        games_per_tiebreak = self.get_games_per_tiebreak()
        armageddon = self.get_armageddon()
        standings_dict = self.get_standings_dict()
        uuids = set()

        for ((item_1, _), (item_2, _)), (score_1, score_2) in zip(self.get_results()[-1], self.get_latest_scores()):
            reverse_participant_standings(
                item_1, item_2, score_1, score_2, standings_dict,
                games, games_per_tiebreak, armageddon, *self.get_totals()
            )
            uuids |= {item_1, item_2}

        level = standings_dict[cast(str, self.get_results()[-1][0][0][0])].level
        if all(standings_dict[uuid].score == self.get_initial_score() for uuid in uuids):
            for uuid in standings_dict.get_alives():
                standings_dict[uuid].level = level
            self.get_auto_advance_history().pop()
        self.set_participants(sorted(self.get_participants(), key=lambda x: standings_dict[x.get_uuid()].seed))
        super().remove_results()

    def seed_participants(self, seeds: list[int] | None = None) -> None:
        assert(self.get_round() == 1)
        if seeds is None:
            if self.is_team_tournament():
                seeds = [i for i in range(len(self.get_participants()))]
                shuffle(seeds)
            else:
                players = cast(list[Player], self.get_participants())
                players_sorted = sort_players_swiss(players)
                seeds = [players.index(player) for player in players_sorted]

        super().seed_participants(seeds)
        standings_dict = self.get_standings_dict()
        for i, uuid in enumerate(self.get_participant_uuids()):
            standings_dict[uuid].seed = i + 1

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        games = self.get_games()
        games_per_tiebreak = self.get_games_per_tiebreak()
        armageddon = self.get_armageddon()
        standings_dict = self.get_standings_dict()

        uuids = standings_dict.get_uuids()
        score_sum = 2 * sum(standings_dict[uuid].score[0] for uuid in uuids) / len(uuids)
        pairing_method = self.get_pairing_method()

        if score_sum == 0 and (len(uuids) & (len(uuids) - 1)):
            through = 2 * (1 << (len(uuids).bit_length() - 1)) - len(uuids)
            uuids = uuids[through:]

        if score_sum == 0 and pairing_method == "Custom":
            pairings = [Pairing(uuids, uuids) for _ in range(int(len(uuids) / 2))]
        elif score_sum == 0:
            pairing_indices = PAIRING_FUNCTIONS[pairing_method](len(uuids), True)
            pairings = [Pairing(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        else:
            pairings = [
                Pairing(item_2, item_1) for (item_1, _), (item_2, _) in self.get_results()[-1] if item_1 in uuids
            ]
            drop_outs = self.get_drop_outs()
            for pairing in pairings:
                item_1, item_2 = pairing
                if item_1 in drop_outs and item_2 in drop_outs:
                    standings_dict[cast(str, item_1)].beaten_by_seed = 0
                    standings_dict[cast(str, item_2)].beaten_by_seed = 0
                    pairings.remove(pairing)

        if armageddon.is_armageddon(games, games_per_tiebreak, int(score_sum + 1)):
            self.set_pairings([
                armageddon.determine_color(cast(str, item_1), cast(str, item_2)) for item_1, item_2 in pairings
            ])
        else:
            self.set_pairings(pairings)

    def drop_out_participants(self, uuids: Sequence[str]) -> None:
        standings_dict = self.get_standings_dict()
        uuids_current = standings_dict.get_uuids()
        if len(set(uuids_current) - set(uuids)) == 0:
            return
        score_sum = 2 * sum(standings_dict[uuid].score[0] for uuid in uuids_current) // len(uuids_current)

        if score_sum == 0:
            for uuid in uuids:
                if standings_dict[uuid].beaten_by_seed is None:
                    standings_dict[uuid].beaten_by_seed = 0

        return super().drop_out_participants(uuids)

    def drop_in_participants(self, participants: Sequence[Participant]) -> None:
        uuids = [participant.get_uuid() for participant in participants]
        standings_dict = self.get_standings_dict()
        current_level = standings_dict.get_current_level()

        for uuid in uuids:
            if uuid in standings_dict and not standings_dict[uuid].was_beaten():
                standings_dict[uuid].level = current_level
                standings_dict[uuid].beaten_by_seed = None
                standings_dict[uuid].score = self.get_initial_score()

        super().drop_in_participants(participants)


def get_scores_mini(score_1: str, score_2: str, score_dict: dict[str, float], factor: int = 1) -> tuple[float, float]:
    if score_1 == '-' == score_2:
        return .5 * factor, .5 * factor
    return score_dict[score_1] * factor, score_dict[score_2] * factor


def get_scores_team(
        score_1: str, score_2: str, result_team: Result_Team,
        score_dict: dict[str, float], score_dict_game: dict[str, float]
) -> tuple[list[float], list[float]]:
    team_points = get_scores_mini(score_1, score_2, score_dict)
    board_points = [
        get_scores_mini(score_1, score_2, score_dict_game) for (_, score_1), (_, score_2) in result_team
    ]
    berlins = [
        get_scores_mini(score_1, score_2, score_dict_game, factor=len(result_team) - i)
        for i, ((_, score_1), (_, score_2)) in enumerate(result_team)
    ]
    return (
        [team_points[0], sum(bo[0] for bo in board_points), sum(be[0] for be in berlins)],
        [team_points[1], sum(bo[1] for bo in board_points), sum(be[1] for be in berlins)]
    )


@TEAM_TOURNAMENT_REGISTRY.register("Knockout (Team)")
class Tournament_Knockout_Team(Tournament_Knockout):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        Tournament.__init__(
            self, participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Knockout (Team)"
        self.parameters = {
            "boards": 8,
            "enforce_lineups": True,
            "games": 1,
            "games_per_tiebreak": 1,
            "pairing_method": ["Slide", "Fold", "Adjacent", "Random"],
            "armageddon": Parameter_Armageddon()
        } | self.parameters
        self.variables = {
            "standings_dict": Variable_Knockout_Standings(dict()),
            "auto_advance_history": []
        } | self.variables
        self.parameters_display = {
            "boards": "Boards",
            "enforce_lineups": "Enforce Lineups",
            "games": "Games per Match",
            "games_per_tiebreak": None,
            "pairing_method": "Pairing Method",
            "armageddon": None
        }

    @staticmethod
    def get_initial_score() -> list[float]:
        return [0., 0., 0.]

    def get_totals(self) -> tuple[list[float], list[float]]:
        games = self.get_games()
        games_per_tiebreak = self.get_games_per_tiebreak()
        boards = self.get_boards()
        return [games, games * boards, games * boards * (boards + 1) / 2], \
               [games_per_tiebreak, games_per_tiebreak * boards, games_per_tiebreak * boards * (boards + 1) / 2]

    def get_latest_scores(self) -> list[tuple[list[float], list[float]]]:
        return [
            get_scores_team(score_1, score_2, result_team, self.get_score_dict(), self.get_score_dict_game())
            for ((item_1, score_1), (item_2, score_2)), result_team
            in zip(self.get_results()[-1], self.get_results_team()[-1])
        ]
