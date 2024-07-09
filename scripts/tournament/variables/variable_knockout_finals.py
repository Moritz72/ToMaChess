from typing import cast, Any
from .variable import Variable
from ..common.bracket_tree import Bracket_Tree, Bracket_Tree_Node
from ..common.pairing_item import Bye_PA
from ..common.type_declarations import Tournament_Data
from ..registries.variable_registry import VARIABLE_REGISTRY
from ..tournaments.tournament_knockout import Tournament_Knockout
from ..utils.functions_tournament_get import get_tournament_type, json_loads_entry

MODES = {
    "Knockout": get_tournament_type("Knockout"),
    "Knockout (Team)": get_tournament_type("Knockout (Team)")
}


@VARIABLE_REGISTRY.register("Variable_Knockout_Finals")
class Variable_Knockout_Finals(list[Tournament_Knockout], Variable):
    def __init__(self, entries: list[Tournament_Data], uuids: list[str], lives: list[int]) -> None:
        entries_load = [json_loads_entry(entry) for entry in entries]
        tournaments = cast(list[Tournament_Knockout], [
            MODES[entry[0]]([], entry[1], entry[2], entry[3], entry[4], entry[5], entry[6], entry[7])
            for entry in entries_load
        ])
        for tournament in tournaments:
            tournament.initialize()
        super().__init__(tournaments)
        self.uuids: list[str] = uuids
        self.lives: list[int] = lives

    def get_class(self) -> str:
        return "Variable_Knockout_Finals"

    def get_dict(self) -> dict[str, Any]:
        return {"entries": [tournament.get_data() for tournament in self], "uuids": self.uuids, "lives": self.lives}

    def get_pair(self) -> tuple[str, str]:
        alives = [uuid for uuid, live in zip(self.uuids, self.lives) if live > 0]
        assert(len(alives) > 1)
        if bool((sum(self.lives) + int(0 < len(self.lives) % 4 < 3)) % 2):
            return alives[0], alives[1]
        return alives[1], alives[0]

    def get_loser(self) -> str | None:
        assert(bool(self))
        current_round = self[-1]
        if not current_round.is_done():
            return None
        alives = current_round.get_standings_dict().get_alives()
        assert(len(alives) == 1)
        return list(set(current_round.get_participant_uuids()) - set(alives))[0]

    def get_uuid_to_standings_table_entry_dict(self) -> dict[str, list[float]]:
        zeros = len(self[0].get_standings_dict()[self.uuids[0]].score) * [0.] if bool(self) else [0.]
        match_numbers = self.calculate_match_numbers()
        standings_table_entry_dict = {
            self.uuids[i]: [0, match_numbers[i], *zeros]
            for i in range(len(self.uuids))
        }
        for i, tournament in enumerate(self):
            for uuid, standing in tournament.get_standings_dict().items():
                standings_table_entry_dict[uuid][2:] = standing.score
        return standings_table_entry_dict

    def get_bracket_tree(self) -> Bracket_Tree:
        if not bool(self):
            return Bracket_Tree(("Bracket Tree", ' ', "F"), Bracket_Tree_Node((Bye_PA(), Bye_PA()), []))
        root = self[-1].get_bracket_tree(0).root
        node = root
        for tournament in self[-2::-1]:
            node_child = tournament.get_bracket_tree(0).root
            node.set_children((node_child,), (True, ))
            node = node_child
        return Bracket_Tree(("Bracket Tree", ' ', "F"), root)

    def set_uuids(self, uuids: list[str]) -> None:
        self.uuids = uuids
        self.lives = [i + 1 for i in range(len(uuids))]

    def is_done(self) -> bool:
        return self.lives.count(0) == len(self.lives) - 1

    def calculate_match_numbers(self) -> list[int]:
        matches = {uuid: 0 for uuid in self.uuids}
        for i, tournament in enumerate(self):
            for uuid in tournament.get_participant_uuids():
                matches[uuid] = i
        return [
            matches[self.uuids[i]] if self.lives[i] == 0
            else len(self) + int(self.is_done()) + self.lives[i] + sum(self.lives[:i]) - max(self.lives[:i] or [0]) - 2
            for i in range(len(self.uuids))
        ]

    def increase_live(self, uuid) -> None:
        self.lives[self.uuids.index(uuid)] += 1

    def decrease_live(self, uuid) -> None:
        self.lives[self.uuids.index(uuid)] -= 1
