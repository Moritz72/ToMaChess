from uuid import uuid4
from os import remove
from json import dumps
from .functions_util import get_directory_by_uuid, write_file


class Player:
    def __init__(self, last_name, first_name="", rating=0, uuid=None):
        if uuid is None:
            self.uuid = str(uuid4())
        else:
            self.uuid = uuid
        self.last_name = last_name
        self.first_name = first_name
        self.rating = rating

    def __str__(self):
        first_name = self.get_first_name()
        last_name = self.get_last_name()
        if first_name:
            return f"{last_name}, {first_name}"
        else:
            return last_name

    def save(self, directory="data/players"):
        write_file(f"{get_directory_by_uuid(directory, self.get_uuid())}.json", dumps(self.__dict__))

    def remove(self, directory="data/players"):
        remove(f"{get_directory_by_uuid(directory, self.get_uuid())}.json")

    def get_uuid(self):
        return self.uuid

    def get_last_name(self):
        return self.last_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def get_first_name(self):
        return self.first_name

    def set_first_name(self, first_name):
        self.first_name = first_name

    def get_rating(self):
        return self.rating

    def set_rating(self, rating):
        self.rating = rating

    def is_valid(self):
        return self.get_last_name() != ""
