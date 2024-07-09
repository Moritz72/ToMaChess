from __future__ import annotations
from typing import Sequence
from .type_declerations import Team_Data
from ..common.object import Object
from ..player.player import Player


class Team(Object):
    def __init__(
            self, members: list[Player], name: str, shallow_member_count: int | None = None,
            uuid: str | None = None, uuid_associate: str = "00000000-0000-0000-0000-000000000001"
    ) -> None:
        super().__init__(name, uuid, uuid_associate)
        self.members: list[Player] = members
        self.shallow_member_count: int = shallow_member_count or len(self.members)

    def copy(self) -> Team:
        return Team(
            [member.copy() for member in self.get_members()],
            self.get_name(), self.get_shallow_member_count(), self.get_uuid(), self.get_uuid_associate()
        )

    def get_members(self) -> list[Player]:
        return self.members

    def get_shallow_member_count(self) -> int:
        return self.shallow_member_count

    def get_member_count(self) -> int:
        return len(self.get_members()) or self.get_shallow_member_count()

    def get_uuid_to_member_dict(self) -> dict[str, Player]:
        return {member.get_uuid(): member for member in self.get_members()}

    def get_uuid_to_name_dict(self) -> dict[str, str]:
        return {member.get_uuid(): member.get_name() for member in self.get_members()}

    def get_uuid_to_number_dict(self) -> dict[str, int]:
        return {member.get_uuid(): i + 1 for i, member in enumerate(self.get_members())}

    def get_data(self) -> Team_Data:
        return self.get_name(), self.get_member_count(), self.get_uuid(), self.get_uuid_associate()

    def set_members(self, members: Sequence[Player]) -> None:
        self.members = list(members)

    def is_valid(self) -> bool:
        return self.get_name() != ""

    def add_members(self, members: Sequence[Player]) -> None:
        self.members.extend(list(members))

    def remove_members_by_uuid(self, uuids: Sequence[str]) -> None:
        self.members = [member for member in self.get_members() if member.get_uuid() not in uuids]

    def apply_uuid_associate(self, uuid_associate: str) -> None:
        super().apply_uuid_associate(uuid_associate)
        for member in self.get_members():
            member.apply_uuid_associate(uuid_associate)
