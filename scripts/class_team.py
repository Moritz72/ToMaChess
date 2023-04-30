from json import dumps
from uuid import uuid4
from os import mkdir
from os.path import exists
from shutil import rmtree
from .functions_util import get_directory_by_uuid, write_file


class Team:
    def __init__(self, name, members=[], uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.name = name
        self.members = members

    def __str__(self):
        return self.name

    def dump_to_json(self):
        data = self.__dict__.copy()
        data["members"] = [member.get_uuid() for member in data["members"]]
        return dumps(data)

    def save(self, directory="data/teams"):
        uuid = self.get_uuid()

        folder_directory = get_directory_by_uuid(directory, uuid)
        if exists(folder_directory):
            rmtree(f"{folder_directory}/members")
        else:
            mkdir(folder_directory)

        mkdir(f"{folder_directory}/members")
        for member in self.get_members():
            member.save(f"data/teams/{uuid}/members")
        write_file(f"{folder_directory}/team.json", self.dump_to_json())

    def remove(self, directory="data/teams"):
        rmtree(f"{get_directory_by_uuid(directory, self.get_uuid())}")

    def get_uuid(self):
        return self.uuid

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_members(self):
        return self.members

    def set_members(self, members):
        self.members = members

    def add_members(self, members):
        self.set_members(self.get_members() + members)

    def remove_member(self, member):
        self.get_members().remove(member)

    def get_rating(self):
        return int(sum(member.get_rating() for member in self.get_members())/len(self.get_members()))

    def is_valid(self):
        return self.get_name() != "" and len(self.get_members()) > 0

    def get_uuid_to_member_dict(self):
        return {member.get_uuid(): member for member in self.get_members()}

    def get_uuid_to_number_dict(self):
        return {member.get_uuid(): i+1 for i, member in enumerate(self.get_members())}
