from json import dumps
from typing import cast
from ..common.functions_util import remove_duplicates
from ..common.object import Object
from ..tournament.tournaments.tournament import Participant, Tournament

MS_Tournament_Data = tuple[str, int, str, bool, int, str, str, str]
MS_Tournament_Data_Loaded = tuple[str, int, list[list[list[tuple[int, int]]]], bool, int, list[list[str]], str, str]


class MS_Tournament(Object):
    def __init__(
            self, stages_tournaments: list[Tournament] | list[list[Tournament]], name: str,
            shallow_participant_count: int | None = None,
            stages_advance_lists: list[list[list[tuple[int, int]]]] | None = None, draw_lots: bool = True,
            stage: int = 0, order: list[list[str]] | None = None, uuid: str | None = None,
            uuid_associate: str = "00000000-0000-0000-0000-000000000003"
    ) -> None:
        super().__init__(name, uuid, uuid_associate)
        if order is not None and stages_tournaments:
            stages_tournaments = cast(list[Tournament], stages_tournaments)
            tournaments_dict = {tournament.get_uuid(): tournament for tournament in stages_tournaments}
            self.stages_tournaments = [[tournaments_dict[uuid] for uuid in uuids] for uuids in order]
        else:
            self.stages_tournaments = cast(list[list[Tournament]], stages_tournaments)
        self.shallow_participant_count: int = shallow_participant_count or len(self.get_participants())
        self.stages_advance_lists: list[list[list[tuple[int, int]]]] = stages_advance_lists or []
        self.draw_lots: bool = draw_lots
        self.order: list[list[str]] = order or []
        self.stage: int = stage

    def get_shallow_participant_count(self) -> int:
        return self.shallow_participant_count

    def get_stages_tournaments(self) -> list[list[Tournament]]:
        return self.stages_tournaments

    def get_stages_advance_lists(self) -> list[list[list[tuple[int, int]]]]:
        return self.stages_advance_lists

    def get_draw_lots(self) -> bool:
        return self.draw_lots

    def get_stage(self) -> int:
        return self.stage

    def get_stages(self) -> int:
        return len(self.stages_tournaments)

    def get_stage_tournaments(self, stage: int) -> list[Tournament]:
        return self.stages_tournaments[stage]

    def get_stage_advance_lists(self, stage: int) -> list[list[tuple[int, int]]]:
        return self.stages_advance_lists[stage]

    def get_current_tournaments(self) -> list[Tournament]:
        return self.get_stage_tournaments(self.stage)

    def get_current_advance_list(self) -> list[list[tuple[int, int]]]:
        return self.get_stage_advance_lists(self.stage + 1)

    def get_tournaments(self) -> list[Tournament]:
        return [tournament for stage_tournaments in self.get_stages_tournaments() for tournament in stage_tournaments]

    def get_participants(self) -> list[Participant]:
        return remove_duplicates([
            participant for stage_tournaments in self.get_stages_tournaments()
            for stage_tournament in stage_tournaments for participant in stage_tournament.get_participants()
        ])

    def get_participant_count(self) -> int:
        return len(self.get_participants()) or self.get_shallow_participant_count()

    def get_data(self) -> MS_Tournament_Data:
        tournament_uuids: list[list[str]] = [
            [tournament.get_uuid() for tournament in stage_tournaments]
            for stage_tournaments in self.get_stages_tournaments()
        ]
        return self.get_name(), self.get_participant_count(), dumps(self.get_stages_advance_lists()), \
            self.get_draw_lots(), self.get_stage(), dumps(tournament_uuids or self.order), \
            self.get_uuid(), self.get_uuid_associate()

    def is_team_tournament(self) -> bool:
        return self.get_stage_tournaments(0)[0].is_team_tournament()

    def is_valid(self) -> bool:
        if not bool(self.stages_tournaments):
            return self.get_name() != ""
        return (
                self.get_name() != "" and
                all(len(self.get_stage_tournaments(i)) > 0 for i in range(self.get_stages())) and
                all(tournament.is_valid() for tournament in self.get_current_tournaments()) and
                all(
                    len(advance_list) > 0 for i in range(self.get_stages() - 1)
                    for advance_list in self.get_stage_advance_lists(i)
                )
        )

    def increment_stage(self) -> None:
        self.stage += 1

    def possess_participants_and_tournaments(self) -> None:
        for participant in self.get_participants():
            participant.apply_uuid_associate(self.get_uuid())
        for stage_tournaments in self.get_stages_tournaments():
            for tournament in stage_tournaments:
                tournament.apply_uuid_associate(self.get_uuid())

    def current_stage_is_done(self) -> bool:
        return all(tournament.is_done() for tournament in self.get_current_tournaments())

    def advance_stage(self) -> None:
        participants_placements = [
            tournament.get_standings().get_placements(self.draw_lots) for tournament in self.get_current_tournaments()
        ]
        participants_next_stage = [[
            participant for tournament, placement in advance_list
            for participant in participants_placements[tournament][placement - 1]
        ] for advance_list in self.get_current_advance_list()]

        self.increment_stage()
        for tournament, participants in zip(self.get_current_tournaments(), participants_next_stage):
            tournament.set_participants(participants)
        if all(not tournament.is_valid() for tournament in self.get_current_tournaments()):
            self.stage -= 1
