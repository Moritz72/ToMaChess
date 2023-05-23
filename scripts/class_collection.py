from uuid import uuid4


class Collection:
    def __init__(self, name, object_type, uuid=None):
        self.name = name
        self.object_type = object_type
        self.uuid = uuid or str(uuid4())

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_object_type(self):
        return self.object_type

    def set_object_type(self, object_type):
        self.object_type = object_type

    def get_uuid(self):
        return self.uuid

    def get_data(self):
        return self.get_name(), self.get_object_type(), self.get_uuid()

    def is_valid(self):
        return self.name != "" and self.object_type in ("Players", "Tournaments", "Teams", "Multi-Stage Tournaments")
