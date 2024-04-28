from typing import Any, Sequence, cast
from .tournament import Participant, Tournament
from ..common.cross_table import Cross_Table
from ..common.pairing import Pairing
from ..common.result import Result
from ..common.result_team import Result_Team
from ..parameters.parameter_tiebreak import Parameter_Tiebreak, get_tiebreak_list
from ..utils.functions_tournament_util import get_score_dict_by_point_system


class Tournament_Scheveningen(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Scheveningen"
        self.parameters = {
            "cycles": 1,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Parameter_Tiebreak(get_tiebreak_list("Wins")),
            "tiebreak_2": Parameter_Tiebreak(get_tiebreak_list("None"))
        } | self.parameters
        self.parameters_display = {
            "cycles": "Cycles",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)")
        }

    def get_score_dict(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system())

    def get_changeable_parameters(self, initial: bool = False) -> dict[str, Any]:
        if initial or not self.is_done():
            return super().get_changeable_parameters(initial)
        return {
            key: value for key, value in super().get_changeable_parameters(initial).items()
            if key not in ("cycles",)
        }

    def get_round_name(self, r: int) -> tuple[str, ...]:
        if self.get_cycles() == 1:
            return super().get_round_name(r)
        half = len(self.get_participants()) // 2
        div, mod = divmod(r - 1, half)
        return "Round", f" {div + 1}.{mod + 1}"

    def get_cycles(self) -> int:
        return cast(int, self.get_parameter("cycles"))

    def get_point_system(self) -> str:
        return cast(str, self.get_parameter("point_system")[0])

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return (
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_1")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_2"))
        )

    def get_cross_table(self) -> Cross_Table:
        uuids = self.get_participant_uuids()
        names = [participant.get_name() for participant in self.get_participants()]
        half = len(uuids) // 2
        uuids_1, uuids_2 = uuids[:half], uuids[half:]
        table = [["" for _ in range(half)] for _ in range(half)]

        for roun in self.get_results():
            for (item_1, score_1), (item_2, score_2) in roun:
                if item_1 in uuids_1 and item_2 in uuids_2:
                    table[uuids_1.index(item_1)][uuids_2.index(item_2)] += score_1
                elif item_1 in uuids_2 and item_2 in uuids_1:
                    table[uuids_1.index(item_2)][uuids_2.index(item_1)] += score_2
        return Cross_Table(cast(list[list[str | None]], table), names[:half], names[half:])

    def is_valid_parameters(self) -> bool:
        half = len(self.get_participants()) // 2
        roun = self.get_round()
        cycles = self.get_cycles()
        return cycles * half >= max(1, roun - 1) or (cycles > 0 and half == 0)

    def is_valid(self) -> bool:
        return super().is_valid() and (len(self.get_participants()) % 2 == 0)

    def is_done(self) -> bool:
        half = len(self.get_participants()) // 2
        return self.get_round() > self.get_cycles() * half

    def is_drop_in_allowed(self) -> bool:
        return False

    def is_add_byes_allowed(self) -> bool:
        return False

    def is_seeding_allowed(self) -> bool:
        return False

    def add_results(self, results: Sequence[Result] | Sequence[Result_Team]) -> None:
        super().add_results(results)
        if self.get_round() != 2:
            return

        results = self.get_results()[-1]
        participant_dict = self.get_uuid_to_participant_dict()
        self.set_participants(
            [participant_dict[item_1] for (item_1, _), (_, _) in results] +
            [participant_dict[item_2] for (_, _), (item_2, _) in results]
        )

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        roun = self.get_round()
        half = len(self.get_participants()) // 2
        uuids = self.get_participant_uuids()

        if roun == 1:
            pairings = [Pairing(uuids, uuids) for _ in range(half)]
            self.set_pairings(pairings)
            return

        div, mod = divmod(roun - 1, half)
        if mod % 2:
            pairs = [(half + i, (i - mod) % half) for i in range(half)]
        else:
            pairs = [(i, half + (i + mod) % half) for i in range(half)]
        if div % 2:
            pairs = [(p_2, p_1) for p_1, p_2 in pairs]
        elif roun == self.get_cycles() * half:
            pairs = [(0, 2 * half - 1)] + [(half + i - 1, i) if i % 2 else (i, half + i - 1) for i in range(1, half)]
        self.set_pairings([Pairing(uuids[p_1], uuids[p_2]) for p_1, p_2 in pairs])
