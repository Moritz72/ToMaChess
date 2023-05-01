from copy import deepcopy
from json import dumps
from uuid import uuid4
from os import mkdir
from os.path import exists
from shutil import rmtree
from .functions_tournament import load_tournament_from_file
from .functions_tournament_2 import get_placements_from_standings
from .functions_util import get_directory_by_uuid, write_file


def make_stage_directory(uuid, stage):
    mkdir(f"{get_directory_by_uuid('data/ms_tournaments', uuid)}/stage_{stage + 1}")


class MS_Tournament:
    def __init__(self, name, stages_tournaments, stages_advance_lists, draw_lots, stage=0, uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.name = name
        self.stages_tournaments = stages_tournaments
        self.stages_advance_lists = stages_advance_lists
        self.draw_lots = draw_lots
        self.stage = stage

    def __str__(self):
        return self.name

    def dump_to_json(self):
        data = deepcopy(self.__dict__)
        data["stages_tournaments"] = [
            [tournament.get_uuid() for tournament in stage] for stage in data["stages_tournaments"]
        ]
        return dumps(data)

    def load_from_json(self, json):
        for i, stage_tournaments in enumerate(json["stages_tournaments"]):
            tournaments = [
                load_tournament_from_file(tournament, f"data/ms_tournaments/{json['uuid']}/stage_{i+1}")
                for tournament in stage_tournaments
            ]
            self.add_stage_tournaments(tournaments)

    def save(self, directory="data/ms_tournaments"):
        uuid = self.get_uuid()
        stages = self.get_stages()

        folder_directory = get_directory_by_uuid(directory, uuid)
        if not exists(folder_directory):
            mkdir(folder_directory)
            for stage in range(stages):
                make_stage_directory(uuid, stage)

        for stage in range(stages):
            for tournament in self.get_tournaments(stage):
                tournament.save(f"{directory}/{uuid}/stage_{stage + 1}")

        write_file(f"{folder_directory}/ms_tournament.json", self.dump_to_json())

    def remove(self, directory="data/ms_tournaments"):
        rmtree(f"{get_directory_by_uuid(directory, self.get_uuid())}")

    def get_uuid(self):
        return self.uuid

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    @staticmethod
    def get_mode():
        return "Multi Stage"

    def get_stage(self):
        return self.stage

    def increment_stage(self):
        self.stage += 1

    def get_stages(self):
        return len(self.stages_tournaments)

    def get_tournaments(self, stage):
        return self.stages_tournaments[stage]

    def get_advance_list(self, stage):
        return self.stages_advance_lists[stage]

    def get_current_tournaments(self):
        return self.get_tournaments(self.stage)

    def get_current_advance_list(self):
        return self.get_advance_list(self.stage)

    def get_participants(self):
        return [pariticipant for tournament in self.stages_tournaments[0]
                for pariticipant in tournament.get_participants()]

    def add_stage_tournaments(self, stage_tournaments):
        self.stages_tournaments.append(stage_tournaments)

    def add_stage_advance_lists(self, stage_advance_lists):
        self.stages_advance_lists.append(stage_advance_lists)

    def is_valid(self):
        return (
            self.get_name() != "" and self.get_stages() > 0 and
            all(len(self.get_tournaments(i)) > 0 for i in range(self.get_stage(), self.get_stages())) and
            all(tournament.is_valid() for tournament in self.get_current_tournaments()) and
            all(
                len(advance_list) > 0
                for i in range(self.get_stages(), self.get_stages()) for advance_list in self.get_advance_list(i)
            )
        )

    def save_tournament(self, stage, i):
        self.stages_tournaments[stage][i].save(f"data/ms_tournaments/{self.get_uuid()}/stage_{stage+1}")

    def current_stage_is_done(self):
        return all(tournament.is_done() for tournament in self.get_current_tournaments())

    def advance_stage(self):
        participants_placements = [
            get_placements_from_standings(tournament.get_standings(), self.draw_lots)
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
