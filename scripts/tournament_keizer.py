from typing import Sequence, Any, cast
from networkx import complete_graph, max_weight_matching
from .tournament import Tournament, Participant
from .pairing import Pairing
from .result import Result
from .player import Player
from .parameter_tiebreak import Parameter_Tiebreak
from .functions_tournament_util import get_score_dict_by_point_system, get_score_dict_keizer
from .db_player import sort_players_by_rating

TB_1 = ["Games", "None", "Games as Black", "Wins", "Wins as Black", "Average Rating", "Direct Encounter"]
TB_2 = ["None", "Games", "Games as Black", "Wins", "Wins as Black", "Average Rating", "Direct Encounter"]


class Tournament_Keizer(Tournament):
    def __init__(
            self, participants: list[Participant], name: str, shallow_participant_count: int | None = None,
            parameters: dict[str, Any] | None = None, variables: dict[str, Any] | None = None,
            order: list[str] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000002"
    ) -> None:
        super().__init__(
            participants, name, shallow_participant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Keizer"
        self.parameters = {
            "rounds": 7,
            "ratio_fl": 3,
            "bye_percentage": 50,
            "no_repeats": True,
            "point_system": ["1 - ½ - 0", "2 - 1 - 0", "3 - 1 - 0"],
            "tiebreak_1": Parameter_Tiebreak(TB_1),
            "tiebreak_2": Parameter_Tiebreak(TB_2),
        } | self.parameters
        self.parameters_display |= {
            "rounds": "Rounds",
            "ratio_fl": "Ratio (First to Last)",
            "bye_percentage": "Score for Byes (%)",
            "no_repeats": "No Pairing Repeats",
            "point_system": "Point System",
            "tiebreak_1": ("Tiebreak", " (1)"),
            "tiebreak_2": ("Tiebreak", " (2)")
        }

    def get_score_dict(self) -> dict[str, float]:
        return get_score_dict_by_point_system(self.get_point_system(), half_bye=True)

    def get_rounds(self) -> int:
        return cast(int, self.get_parameter("rounds"))

    def get_ratio_fl(self) -> int:
        return cast(int, self.get_parameter("ratio_fl"))

    def get_bye_percentage(self) -> int:
        return cast(int, self.get_parameter("bye_percentage"))

    def get_no_repeats(self) -> bool:
        return cast(bool, self.get_parameter("no_repeats"))

    def get_point_system(self) -> str:
        return cast(str, self.get_parameter("point_system")[0])

    def get_tiebreaks(self) -> tuple[Parameter_Tiebreak, ...]:
        return (
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_1")),
            cast(Parameter_Tiebreak, self.get_parameter("tiebreak_2"))
        )

    def get_simple_scores(self) -> dict[str, float]:
        uuids = self.get_participant_uuids(drop_outs=False, byes=True)
        p_max = int((len(uuids) - 1) * (self.get_ratio_fl() / (self.get_ratio_fl() - 1)))
        return get_score_dict_keizer(uuids, self.get_score_dict(), self.get_results(), p_max, self.get_bye_percentage())

    def is_valid_parameters(self) -> bool:
        return self.get_rounds() >= max(1, self.get_round() - 1) and self.get_ratio_fl() > 1

    def is_done(self) -> bool:
        return self.get_round() > self.get_rounds()

    def seat_participants(self) -> None:
        self.set_participants(sort_players_by_rating(cast(list[Player], self.get_participants())))

    def load_pairings(self) -> None:
        if bool(self.get_pairings()) or self.is_done():
            return
        uuids = [participant.get_uuid() for participant in self.get_standings().participants]
        uuids = [uuid for uuid in uuids if uuid not in self.get_byes()]
        n = len(uuids)
        w_factor = (n * n * n * n, n * n, 1)
        uuid_to_index = {uuid: uuids.index(uuid) for uuid in uuids}
        white_dict, black_dict = self.get_results().get_white_black_stats()
        edges = [
            (uuid_to_index[item_1], uuid_to_index[item_2])
            for result_list in self.get_results() for (item_1, _), (item_2, _) in result_list
            if item_1 in uuids and item_2 in uuids
        ] if self.get_no_repeats() else []

        pairing_graph = complete_graph(n)
        pairing_graph.remove_edges_from(edges)
        for i, j in pairing_graph.edges:
            pairing_graph[i][j]["weight"] = w_factor[0] + (2 * n - i - j) * w_factor[1] + (n - abs(i - j)) * w_factor[2]
        maximal_matching = max_weight_matching(pairing_graph)

        pairings = []
        for i, j in sorted(maximal_matching, key=lambda x: min(x)):
            uuid_1, uuid_2 = uuids[i], uuids[j]
            lower = uuid_to_index[uuid_1] > uuid_to_index[uuid_2]
            more_white_1 = white_dict[uuid_1] - black_dict[uuid_1] if uuid_1 in white_dict else 0
            more_white_2 = white_dict[uuid_2] - black_dict[uuid_2] if uuid_2 in white_dict else 0
            if more_white_1 < more_white_2 or (more_white_1 == more_white_2 and lower):
                pairings.append(Pairing(uuid_1, uuid_2))
            else:
                pairings.append(Pairing(uuid_2, uuid_1))

        for i in set(range(len(uuids))) - set(i for i, _ in maximal_matching) - set(i for _, i in maximal_matching):
            pairings.append(Pairing(uuids[i], ""))
        for uuid in self.get_byes():
            pairings.append(Pairing(uuid, "bye"))
        self.set_pairings(pairings)

    def drop_in_participants(self, participants: Sequence[Participant] | None = None) -> bool:
        participants = participants or []
        super().drop_in_participants(participants)
        self.seat_participants()
        uuids = [participant.get_uuid() for participant in participants]
        for round_results in self.get_results():
            uuids_round = [uuid for (uuid, _), (_, _) in round_results] + [uuid for (_, _), (uuid, _) in round_results]
            for uuid in set(uuids) - set(uuids_round):
                round_results.append(Result((uuid, 'b'), ("bye", '-')))
        return True

    def add_byes(self, uuids: Sequence[str] | None = None) -> bool:
        if uuids is not None:
            self.set_byes(list(uuids))
        return True
