from json import dumps
from uuid import uuid4
from os import mkdir
from os.path import exists
from shutil import rmtree
from .functions_util import get_root_directory, write_file


def get_directory(uuid):
    return f"{get_root_directory()}/data/teams/{uuid}"


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

    def save(self):
        uuid = self.get_uuid()

        if exists(get_directory(uuid)):
            rmtree(f"{get_directory(uuid)}/members")
        else:
            mkdir(get_directory(uuid))

        mkdir(f"{get_directory(uuid)}/members")
        for member in self.get_members():
            member.save(f"data/teams/{uuid}/members")
        write_file(f"{get_directory(uuid)}/team.json", self.dump_to_json())

    def remove(self):
        rmtree(f"{get_directory(self.get_uuid())}")

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

    def is_valid(self):
        return self.get_name() != "" and len(self.get_members()) > 0
