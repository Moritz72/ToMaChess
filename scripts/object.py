from __future__ import annotations
from abc import abstractmethod
from typing import Any
from uuid import uuid4


class Object:
    def __init__(self, name: str, uuid: str | None, uuid_associate: str | None) -> None:
        self.name: str = name
        self.uuid: str = uuid or str(uuid4())
        self.uuid_associate: str = uuid_associate or ""

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Object):
            return NotImplemented
        return self.get_uuid_tuple() == other.get_uuid_tuple()

    def __hash__(self) -> int:
        return hash(self.get_uuid_tuple())

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def get_name(self) -> str:
        return self.name

    def get_uuid(self) -> str:
        return self.uuid

    def get_uuid_associate(self) -> str:
        return self.uuid_associate

    def get_uuid_tuple(self) -> tuple[str, str]:
        return self.uuid, self.uuid_associate

    @abstractmethod
    def get_data(self) -> tuple[Any, ...]:
        pass

    def set_name(self, name: str) -> None:
        self.name = name

    def set_uuid_associate(self, uuid_associate: str) -> None:
        self.uuid_associate = uuid_associate

    @abstractmethod
    def is_valid(self) -> bool:
        pass

    def reload_uuid(self) -> None:
        self.uuid = str(uuid4())

    def apply_uuid_associate(self, uuid_associate: str) -> None:
        self.set_uuid_associate(uuid_associate)
