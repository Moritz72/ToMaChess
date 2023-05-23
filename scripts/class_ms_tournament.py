from uuid import uuid4
from json import dumps
from .functions_tournament_util import get_placements_from_standings


class MS_Tournament:
    def __init__(
            self, participants, stages_tournaments, name, shallow_participant_count=None, stages_advance_lists=[],
            draw_lots=True, stage=0, order=None, uuid=None, uuid_associate="00000000-0000-0000-0000-000000000003"
    ):
        self.participants = participants
        if order is not None and stages_tournaments:
            tournaments_dict = {tournament.get_uuid(): tournament for tournament in stages_tournaments}
            self.stages_tournaments = [[tournaments_dict[uuid] for uuid in uuids] for uuids in order]
        else:
            self.stages_tournaments = stages_tournaments
        self.name = name
        self.shallow_participant_count = shallow_participant_count
        self.stages_advance_lists = stages_advance_lists
        self.draw_lots = draw_lots
        self.stage = stage
        self.uuid = uuid or str(uuid4())
        self.uuid_associate = uuid_associate

    def __str__(self):
        return self.name

    def possess_participants_and_tournaments(self):
        for participant in self.get_participants():
            participant.set_uuid_associate(self.get_uuid())
        for stage_tournaments in self.get_stages_tournaments():
            for tournament in stage_tournaments:
                tournament.set_uuid_associate(self.get_uuid())

    def get_uuid(self):
        return self.uuid

    def get_uuid_associate(self):
        return self.uuid_associate

    def set_uuid_associate(self, uuid_associate):
        self.uuid_associate = uuid_associate

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_shallow_participant_count(self):
        return self.shallow_participant_count

    def get_stages_tournaments(self):
        return self.stages_tournaments

    def get_stages_advance_list(self):
        return self.stages_advance_lists

    def get_draw_lots(self):
        return self.draw_lots

    def get_stage(self):
        return self.stage

    def increment_stage(self):
        self.stage += 1

    def get_stages(self):
        return len(self.stages_tournaments)

    def get_stage_tournaments(self, stage):
        return self.stages_tournaments[stage]

    def get_stage_advance_list(self, stage):
        return self.stages_advance_lists[stage]

    def get_current_tournaments(self):
        return self.get_stage_tournaments(self.stage)

    def get_current_advance_list(self):
        return self.get_stage_advance_list(self.stage)

    def get_participants(self):
        return self.participants

    def get_participant_count(self):
        return len(self.get_participants()) or self.shallow_participant_count

    def get_data(self):
        return self.get_name(), self.get_participant_count(), dumps(self.get_stages_advance_list()),\
               self.get_draw_lots(), self.get_stage(),\
               dumps([
                   [tournament.get_uuid() for tournament in stage_tournaments]
                   for stage_tournaments in self.get_stages_tournaments()
               ]),\
               self.get_uuid(), self.get_uuid_associate()

    def is_valid(self):
        return (
                self.get_name() != "" and self.get_stages() > 0 and
                all(len(self.get_stage_tournaments(i)) > 0 for i in range(self.get_stage(), self.get_stages())) and
                all(tournament.is_valid() for tournament in self.get_current_tournaments()) and
                all(
                    len(advance_list) > 0 for i in range(self.get_stages(), self.get_stages())
                    for advance_list in self.get_stage_advance_list(i)
                )
        )

    def current_stage_is_done(self):
        return all(tournament.is_done() for tournament in self.get_current_tournaments())

    def advance_stage(self):
        participants_placements = [
            get_placements_from_standings(tournament.get_standings(), self.get_draw_lots())
            for tournament in self.get_current_tournaments()
        ]
        participants_next_stage = [
            [
                participant for tournament, placement in advance_list
                for participant in participants_placements[tournament][placement-1]
            ]
            for advance_list in self.get_current_advance_list()
        ]

        self.increment_stage()
        for tournament, participants in zip(self.get_current_tournaments(), participants_next_stage):
            tournament.set_participants(participants)
