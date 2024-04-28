from random import shuffle
from typing import Any, Sequence, cast
from .tournament import Participant, Tournament
from ..common.pairing import Pairing
from ..common.result import Result
from ..common.result_team import Result_Team
from ..parameters.parameter_tiebreak import Parameter_Tiebreak, get_tiebreak_list
from ..utils.functions_pairing import PAIRING_FUNCTIONS_ROUND_ROBIN
from ..utils.functions_tournament_util import get_score_dict_by_point_system
from ...common.functions_util import has_duplicates


class Tournament_Round_Robin(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Round Robin"
        self.parameters = {
            "cycles": 1,
            "pairing_method": ["Cycle", "Berger"],
            "custom_seeding": False,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Direct Encounter")),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("Sonneborn-Berger")),
            "tiebreak_3": Parameter_Tiebreak(get_tiebreak_list("None")),
            "tiebreak_4": Parameter_Tiebreak(get_tiebreak_list("None"))
        } | self.parameters
        self.parameters_display = {
            "cycles": "Cycles",
            "pairing_method": "Pairing Method",
            "custom_seeding": "Custom Seeding",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def get_score_dict(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system())

    def get_changeable_parameters(self, initial: bool = False) -> dict[str, Any]:
        if initial:
            return super().get_changeable_parameters(initial)
        return {
            key: value for key, value in super().get_changeable_parameters(initial).items()
            if key not in ("pairing_method",)
        }

    def get_round_name(self, r: int) -> tuple[str, ...]:
        if self.get_cycles() == 1:
            return super().get_round_name(r)
        participant_number = len(self.get_participants())
        div, mod = divmod(r - 1, participant_number + (participant_number % 2) - 1)
        return "Round", f" {div + 1}.{mod + 1}"

    def get_cycles(self) -> int:
        return cast(int, self.get_parameter("cycles"))

    def get_pairing_method(self) -> str:
        return cast(str, self.get_parameter("pairing_method")[0])

    def get_custom_seeding(self) -> bool:
        return cast(bool, self.get_parameter("custom_seeding"))

    def get_point_system(self) -> str:
        return cast(str, self.get_parameter("point_system")[0])

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return (
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_1")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_2")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_3")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_4"))
        )

    def is_valid_parameters(self) -> bool:
        participant_number = len(self.get_participants())
        roun = self.get_round()
        cycles = self.get_cycles()
        if participant_number % 2:
            return cycles * participant_number >= max(1, roun - 1)
        return cycles * (participant_number - 1) >= max(1, roun - 1) or (cycles > 0 and participant_number == 0)

    def is_valid_pairings(self, pairings: Sequence[Pairing]) -> bool:
        assert(all(pairing.is_fixed() for pairing in pairings))
        return not has_duplicates([item for item, _ in pairings] + [item for _, item in pairings])

    def is_done(self) -> bool:
        participant_number = len(self.get_participants())
        if participant_number % 2:
            return self.get_round() > self.get_cycles() * participant_number
        return self.get_round() > self.get_cycles() * (participant_number - 1)

    def is_drop_in_allowed(self) -> bool:
        return False

    def is_add_byes_allowed(self) -> bool:
        return False

    def is_seeding_allowed(self) -> bool:
        return self.get_round() == 1 and not self.get_custom_seeding()

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        super().add_results(results)
        if self.get_round() != 2 or not self.get_custom_seeding():
            return

        results = self.get_results()[-1]
        uuid_to_seed = dict()
        pairing_indices = PAIRING_FUNCTIONS_ROUND_ROBIN[self.get_pairing_method()](len(self.get_participants()), 1)
        for ((item_1, _), (item_2, _)), (i_1, i_2) in zip(results, pairing_indices):
            uuid_to_seed[cast(str, item_1)], uuid_to_seed[cast(str, item_2)] = i_1, i_2
        self.set_participants(sorted(
            self.get_participants(), key=lambda x: uuid_to_seed[x.get_uuid()] if x.get_uuid() in uuid_to_seed else 0
        ))

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        roun = self.get_round()
        participant_number = len(self.get_participants())
        uuids = self.get_participant_uuids()

        if roun == 1 and self.get_custom_seeding():
            pairings = [Pairing(uuids, uuids) for _ in range(participant_number // 2)]
            self.set_pairings(pairings)
            return

        if roun == 1:
            shuffle(self.get_participants())

        uuids = self.get_participant_uuids()
        pairing_method = PAIRING_FUNCTIONS_ROUND_ROBIN[self.get_pairing_method()]
        pairing_indices = pairing_method(participant_number, roun)
        pairings = [Pairing(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        self.set_pairings(pairings)


class Tournament_Round_Robin_Team(Tournament_Round_Robin):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        Tournament.__init__(
            self, participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Round Robin (Team)"
        self.parameters = {
            "boards": 8,
            "enforce_lineups": True,
            "cycles": 1,
            "pairing_method": ["Cycle", "Berger"],
            "custom_seeding": False,
            "point_system": ["2 - 1 - 0", "1 - ½ - 0", "3 - 1 - 0"],
            "point_system_game": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Board Points", team=True)),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("Direct Encounter", team=True)),
            "tiebreak_3": Parameter_Tiebreak(get_tiebreak_list("Sonneborn-Berger", team=True)),
            "tiebreak_4": Parameter_Tiebreak(get_tiebreak_list("None", team=True))
        } | self.parameters
        self.parameters_display = {
            "boards": "Boards",
            "enforce_lineups": "Enforce Lineups",
            "cycles": "Cycles",
            "pairing_method": "Pairing Method",
            "custom_seeding": None,
            "point_system": "Point System (Match)",
            "point_system_game": "Point System (Game)",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)"),
            "tiebreak_3": ("Tiebreak", " (3)"),
            "tiebreak_4": ("Tiebreak", " (4)")
        }

    def get_score_dict_game(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system_game())

    def get_point_system_game(self) -> str:
        return cast(str, self.get_parameter("point_system_game")[0])
