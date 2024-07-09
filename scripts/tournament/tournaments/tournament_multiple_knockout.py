from typing import Any, Sequence, cast
from .tournament import Tournament
from .tournament_knockout import Tournament_Knockout, Tournament_Knockout_Team
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
from ..variables.variable_knockout_brackets import Variable_Knockout_Brackets
from ..variables.variable_knockout_finals import Variable_Knockout_Finals
from ..variables.variable_results import Variable_Results
from ..variables.variable_results_team import Variable_Results_Team


@TOURNAMENT_REGISTRY.register("Multiple Knockout")
class Tournament_Multiple_Knockout(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Multiple Knockout"
        self.parameters = {
            "multiplicity": 2,
            "with_finals": True,
            "games": 2,
            "games_per_tiebreak": 2,
            "pairing_method": ["Fold", "Slide", "Adjacent", "Random", "Custom"],
            "armageddon": Parameter_Armageddon()
        } | self.parameters
        self.variables = {
            "brackets": Variable_Knockout_Brackets([], [0]),
            "finals": Variable_Knockout_Finals([], [], []),
        } | self.variables
        self.parameters_display = {
            "multiplicity": "Multiplicity",
            "with_finals": "With Finals",
            "games": "Games per Match",
            "games_per_tiebreak": "Games per Tiebreak",
            "pairing_method": "Pairing Method",
            "armageddon": "Armageddon"
        }

    def get_results(self) -> Variable_Results:
        brackets = self.get_brackets()
        bracket_indices = brackets.get_indices()
        bracket_counts = [bracket_indices[:i].count(index) for i, index in enumerate(bracket_indices[:-1])]
        bracket_results = [bracket.get_results() for bracket in brackets]

        results = Variable_Results([])
        results.extend([bracket_results[index][count] for index, count in zip(bracket_indices, bracket_counts)])
        for tournament in self.get_finals():
            results.extend(tournament.get_results())
        return results

    def get_results_team(self) -> Variable_Results_Team:
        if not self.is_team_tournament():
            return NotImplemented

        brackets = self.get_brackets()
        bracket_indices = brackets.get_indices()
        bracket_counts = [bracket_indices[:i].count(index) for i, index in enumerate(bracket_indices[:-1])]
        bracket_results = [bracket.get_results_team() for bracket in brackets]

        results = Variable_Results_Team([])
        results.extend([bracket_results[index][count] for index, count in zip(bracket_indices, bracket_counts)])
        for tournament in self.get_finals():
            results.extend(tournament.get_results_team())
        return results

    def get_changeable_parameters(self, initial: bool = False) -> dict[str, Any]:
        if initial:
            return super().get_changeable_parameters(initial)
        if not bool(self.get_finals()):
            return dict({"with_finals": self.get_with_finals()})
        return dict()

    def get_round_name(self, r: int) -> tuple[str, ...]:
        brackets = self.get_brackets()
        indices = brackets.get_indices()

        if r > len(indices) - int(bool(self.get_finals())):
            finals = self.get_finals()
            r -= len(indices) - 1
            for index, tournament in enumerate(finals):
                rounds = tournament.get_round() - int(index < len(finals) - 1)
                if r <= rounds:
                    return ("F", f"{index + 1}", ' ') + tournament.get_round_name(r)
                r -= rounds

        index = indices[r - 1]
        return ("B", f"{index + 1}", ' ') + brackets[index].get_round_name(indices[:r].count(index))

    def get_standings(self, category_range: Category_Range | None = None) -> Standings_Table:
        headers = ["Name", "Bracket", "Matches", "Match Points"]
        if self.is_team_tournament():
            headers.extend(["Board Points", "Berlin Rating"])
        standings_table_entry_dict = self.get_brackets().get_uuid_to_standings_table_entry_dict()
        standings_table_entry_dict |= self.get_finals().get_uuid_to_standings_table_entry_dict()
        if self.is_team_tournament():
            for entry in standings_table_entry_dict.values():
                entry[2] *= 2

        participants = self.get_participants()
        if category_range is not None:
            participants = category_range.filter_list(participants)
        uuids = [participant.get_uuid() for participant in participants]

        standings_table = Standings_Table(participants, [standings_table_entry_dict[uuid] for uuid in uuids], headers)
        standings_table.set_key(0, lambda x: -x)
        return standings_table

    def get_multiplicity(self) -> int:
        return cast(int, self.get_parameter("multiplicity"))

    def get_with_finals(self) -> bool:
        return cast(bool, self.get_parameter("with_finals"))

    def get_games(self) -> int:
        return cast(int, self.get_parameter("games"))

    def get_games_per_tiebreak(self) -> int:
        return cast(int, self.get_parameter("games_per_tiebreak"))

    def get_pairing_method(self) -> str:
        return cast(str, self.get_parameter("pairing_method")[0])

    def get_armageddon(self) -> Parameter_Armageddon:
        return cast(Parameter_Armageddon, self.get_parameter("armageddon"))

    def get_brackets(self) -> Variable_Knockout_Brackets:
        return cast(Variable_Knockout_Brackets, self.get_variable("brackets"))

    def get_finals(self) -> Variable_Knockout_Finals:
        return cast(Variable_Knockout_Finals, self.get_variable("finals"))

    def get_blank_tournament(self) -> Tournament_Knockout:
        parameters = {
            "games": self.get_games(),
            "games_per_tiebreak": self.get_games_per_tiebreak(),
            "pairing_method": [self.get_pairing_method()],
            "armageddon": self.get_armageddon()
        }
        return Tournament_Knockout([], "_", parameters=parameters)

    def get_cross_table(self, i: int) -> Cross_Table:
        return NotImplemented

    def get_cross_tables(self) -> int:
        return 0

    def get_bracket_tree(self, i: int) -> Bracket_Tree:
        assert(i < self.get_bracket_trees())
        brackets = self.get_brackets()
        if i < len(brackets):
            return brackets.get_bracket_tree(i)
        return self.get_finals().get_bracket_tree()

    def get_bracket_trees(self) -> int:
        return len(self.get_brackets()) + int(self.get_with_finals())

    def set_brackets(self, brackets: Variable_Knockout_Brackets) -> None:
        self.set_variable("brackets", brackets)

    def is_valid_parameters(self) -> bool:
        return self.get_multiplicity() > 1 and self.get_games() > 0 and self.get_games_per_tiebreak() > 0

    def is_valid(self) -> bool:
        return super().is_valid() and self.get_participant_count() > self.get_multiplicity()

    def is_valid_pairings(self, pairings: Sequence[Pairing]) -> bool:
        return self.get_brackets().get_current_bracket().is_valid_pairings(pairings)

    def is_done(self) -> bool:
        return self.get_brackets().is_done() and (not self.get_with_finals() or self.get_finals().is_done())

    def is_drop_in_allowed(self) -> bool:
        return False

    def is_drop_out_allowed(self) -> bool:
        return False

    def is_add_byes_allowed(self) -> bool:
        return False

    def is_seeding_allowed(self) -> bool:
        return self.get_round() == 1

    def initialize(self) -> None:
        super().initialize()
        participants = self.get_participants()
        for bracket in self.get_brackets():
            bracket.set_participants(participants, from_order=True)
        for tournament in self.get_finals():
            tournament.set_participants(participants, from_order=True)

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        finals = self.get_finals()
        if bool(finals):
            participant_dict = self.get_uuid_to_participant_dict()
            finals[-1].add_results(results)
            loser = finals.get_loser()
            if loser is not None:
                finals.decrease_live(loser)
                if not finals.is_done():
                    finals.append(self.get_blank_tournament())
                    finals[-1].set_participants([participant_dict[uuid] for uuid in finals.get_pair()])
        else:
            self.get_brackets().add_results(results)

        self.set_pairings([])
        self.set_round(self.get_round() + 1)

    def remove_results(self) -> None:
        self.set_round(self.get_round() - 1)
        self.set_pairings([])
        finals = self.get_finals()

        if bool(finals):
            if not finals.is_done():
                current_round = finals[-1]
                if current_round.get_round() > 1:
                    current_round.remove_results()
                    return
                finals.pop()
            if bool(finals):
                loser = finals.get_loser()
                if loser is not None:
                    finals.increase_live(loser)
                finals[-1].remove_results()
            else:
                self.get_brackets().remove_results()
        else:
            self.get_brackets().remove_results()

    def seed_participants(self, seeds: list[int] | None = None) -> None:
        for bracket in self.get_brackets():
            bracket.seed_participants(seeds)

    def load_pairings(self) -> None:
        if not bool(self.get_brackets()):
            self.initialize_brackets()
        if bool(self.get_pairings()) or self.is_done():
            return
        if not self.get_brackets().is_done():
            current_bracket = self.get_brackets().get_current_bracket()
            current_bracket.load_pairings()
            self.set_pairings(current_bracket.get_pairings())
        elif self.get_with_finals():
            if not bool(self.get_finals()):
                self.initialize_finals()
            current_round = self.get_finals()[-1]
            current_round.load_pairings()
            self.set_pairings(current_round.get_pairings())

    def initialize_brackets(self) -> None:
        blank_tournament = self.get_blank_tournament()
        self.set_brackets(Variable_Knockout_Brackets(self.get_multiplicity() * [blank_tournament.get_data()], [0]))
        brackets = self.get_brackets()

        for i, bracket in enumerate(brackets):
            bracket.reload_uuid()
            bracket.set_participants(self.get_participants())
            bracket.seed_participants()
        brackets.set_beaten_by_dummy()

    def initialize_finals(self) -> None:
        participant_dict = self.get_uuid_to_participant_dict()
        multiplity = self.get_multiplicity()
        brackets = self.get_brackets()
        finals = self.get_finals()
        uuids = [brackets.get_bracket_uuids(multiplity - i - 1)[0] for i in range(multiplity)]
        finals.set_uuids(uuids)
        finals.append(self.get_blank_tournament())
        finals[-1].set_participants([participant_dict[uuid] for uuid in finals.get_pair()])


@TEAM_TOURNAMENT_REGISTRY.register("Multiple Knockout (Team)")
class Tournament_Multiple_Knockout_Team(Tournament_Multiple_Knockout):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        Tournament.__init__(
            self, participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Multiple Knockout (Team)"
        self.parameters = {
            "boards": 8,
            "enforce_lineups": True,
            "multiplicity": 2,
            "with_finals": True,
            "games": 1,
            "games_per_tiebreak": 1,
            "pairing_method": ["Fold", "Slide", "Adjacent", "Random"],
            "armageddon": Parameter_Armageddon()
        } | self.parameters
        self.variables = {
            "brackets": Variable_Knockout_Brackets([], [0]),
            "finals": Variable_Knockout_Finals([], [], []),
        } | self.variables
        self.parameters_display = {
            "boards": "Boards",
            "enforce_lineups": "Enforce Lineups",
            "multiplicity": "Multiplicity",
            "with_finals": "With Finals",
            "games": "Games per Match",
            "games_per_tiebreak": "Games per Tiebreak",
            "pairing_method": "Pairing Method",
            "armageddon": "Armageddon"
        }

    def get_blank_tournament(self) -> Tournament_Knockout:
        parameters = {
            "boards": self.get_boards(),
            "enforce_lineups": self.get_enforce_lineups(),
            "games": self.get_games(),
            "games_per_tiebreak": self.get_games_per_tiebreak(),
            "pairing_method": [self.get_pairing_method()],
            "armageddon": self.get_armageddon()
        }
        return Tournament_Knockout_Team([], "_", parameters=parameters)
