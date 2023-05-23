from uuid import uuid4


class Team:
    def __init__(
            self, members, name, shallow_member_count=None, uuid=None,
            uuid_associate="00000000-0000-0000-0000-000000000001"
    ):
        self.name = name
        self.members = members
        self.shallow_member_count = shallow_member_count
        self.uuid = uuid or str(uuid4())
        self.uuid_associate = uuid_associate

    def __str__(self):
        return self.name

    def copy(self):
        return Team(
            [member.copy() for member in self.get_members()],
            self.get_name(), self.get_shallow_member_count(), self.get_uuid(), self.get_uuid_associate()
        )

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

    def get_members(self):
        return self.members

    def set_members(self, members):
        self.members = members

    def add_members(self, members):
        self.members.extend(members)

    def remove_member(self, member):
        self.members.remove(member)

    def get_shallow_member_count(self):
        return self.shallow_member_count

    def set_shallow_member_count(self, count):
        self.shallow_member_count = count

    def get_member_count(self):
        return len(self.get_members()) or self.get_shallow_member_count()

    def get_data(self):
        return self.get_name(), self.get_member_count(), self.get_uuid(), self.get_uuid_associate()

    def is_valid(self):
        return self.get_name() != ""

    def get_uuid_to_member_dict(self):
        return {member.get_uuid(): member for member in self.get_members()}

    def get_uuid_to_number_dict(self):
        return {member.get_uuid(): i + 1 for i, member in enumerate(self.get_members())}
