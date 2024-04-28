from ..common.object import Object

Colection_Data = tuple[str, str, str]


class Collection(Object):
    def __init__(self, name: str, object_type: str, uuid: str | None = None) -> None:
        super().__init__(name, uuid, None)
        self.object_type: str = object_type

    def get_object_type(self) -> str:
        return self.object_type

    def get_data(self) -> Colection_Data:
        return self.get_name(), self.get_object_type(), self.get_uuid()

    def set_object_type(self, object_type: str) -> None:
        self.object_type = object_type

    def is_valid(self) -> bool:
        return bool(self.name) and self.object_type in ("Players", "Tournaments", "Teams", "Multi-Stage Tournaments")
