from abc import abstractmethod
from typing import Sequence, TypeVar, Generic
from ..common.object import Object

T = TypeVar('T', bound=Object)


class DB_Object(Generic[T]):
    def __init__(self, obj_type: str = "", table_name: str = "") -> None:
        self.type: str = obj_type
        self.table_name: str = table_name

    def table(self, table_root: str) -> str:
        return table_root + self.table_name

    @abstractmethod
    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[T]:
        pass

    @abstractmethod
    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[T]:
        pass

    @abstractmethod
    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[T]:
        pass

    @abstractmethod
    def add_list(self, table_root: str, objs: Sequence[T], shallow: bool = False) -> None:
        pass

    @abstractmethod
    def update_list(self, table_root: str, objs: Sequence[T], shallow: bool = False) -> None:
        pass

    @abstractmethod
    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        pass

    @abstractmethod
    def remove_list(self, table_root: str, objs: Sequence[T]) -> None:
        pass
