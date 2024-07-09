from __future__ import annotations
from typing import TYPE_CHECKING, Type
from json import loads
from ..common.type_declarations import Participant, Tournament_Data, Tournament_Data_Loaded
from ..registries.tournament_registry import TEAM_TOURNAMENT_REGISTRY, TOURNAMENT_REGISTRY
if TYPE_CHECKING:
    from ..tournaments.tournament import Tournament


def json_loads_entry(entry: Tournament_Data) -> Tournament_Data_Loaded:
    return entry[0], entry[1], entry[2], loads(entry[3]), loads(entry[4]), loads(entry[5]), entry[6], entry[7]


def get_tournament_type(mode: str) -> Type[Tournament]:
    tournament_type = TOURNAMENT_REGISTRY.get(mode) or TEAM_TOURNAMENT_REGISTRY.get(mode)
    assert (tournament_type is not None)
    return tournament_type


def get_tournament(participants: list[Participant], entry: Tournament_Data) -> Tournament:
    load = json_loads_entry(entry)
    tournament_type = get_tournament_type(entry[0])
    tournament = tournament_type(participants, load[1], load[2], load[3], load[4], load[5], load[6], load[7])
    tournament.initialize()
    return tournament


def get_blank_tournament(mode: str) -> Tournament:
    tournament_type = get_tournament_type(mode)
    tournament = tournament_type([], "")
    tournament.initialize()
    return tournament
