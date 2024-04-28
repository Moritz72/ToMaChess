from typing import Sequence
from .db_object import DB_Object
from .manager_database import MANAGER_DATABASE
from ..collection.collection import Collection, Colection_Data

COLLECTION_ATTRIBUTE_LIST = ["Name", "Type"]
COLLECTION_COLUMNS = ("name", "object_type", "uuid")


def is_default(collection: Collection) -> bool:
    return collection.get_name() == "Default"


def sort_collections(collections: Sequence[Collection]) -> list[Collection]:
    return sorted(collections, key=lambda x: (not is_default(x), x.get_name()))


def filter_default(collections: Sequence[Collection]) -> list[Collection]:
    return [collection for collection in collections if not is_default(collection)]


def collection_exists(table_root: str, uuid: str) -> bool:
    return MANAGER_DATABASE.entry_exists(f"{table_root}collections", ("uuid",), (uuid,))


def load_collections_by_type(table_root: str, object_type: str) -> list[Collection]:
    if object_type not in ("Player", "Tournament", "Team", "Multi-Stage Tournament"):
        return []
    entries: list[Colection_Data] = MANAGER_DATABASE.get_entries(
        f"{table_root}collections", ("object_type",), (object_type + 's',)
    )
    return sort_collections([Collection(*entry) for entry in entries])


class DB_Collection(DB_Object[Collection]):
    def __init__(self) -> None:
        super().__init__(obj_type="Collection", table_name="collections")

    def load_all(self, table_root: str, uuid_associate: str, shallow: bool = False) -> list[Collection]:
        MANAGER_DATABASE.cursor.execute(f"SELECT * FROM {self.table(table_root)}")
        entries: list[Colection_Data] = MANAGER_DATABASE.cursor.fetchall()
        return sort_collections([Collection(*entry) for entry in entries])

    def load_list(
            self, table_root: str, uuid_list: Sequence[str], uuid_associate_list: Sequence[str], shallow: bool = False
    ) -> list[Collection]:
        return NotImplemented

    def load_like(
            self, table_root: str, uuid_associate: str, name: str, limit: int | None, shallow: bool = False
    ) -> list[Collection]:
        entries: list[Colection_Data] = MANAGER_DATABASE.get_entries_like(
            self.table(table_root), tuple(), tuple(), ("name",), (name,), ("object_type", "name"), (True, True), limit
        )
        return sort_collections([Collection(*entry) for entry in entries])

    def add_list(self, table_root: str, collections: Sequence[Collection], shallow: bool = False) -> None:
        collections = filter_default(collections)
        MANAGER_DATABASE.add_entries(
            self.table(table_root), COLLECTION_COLUMNS, [collection.get_data() for collection in collections]
        )

    def update_list(self, table_root: str, collections: Sequence[Collection], shallow: bool = False) -> None:
        collections = filter_default(collections)
        MANAGER_DATABASE.update_entries(
            self.table(table_root), ("uuid",), [(collection.get_uuid(),) for collection in collections],
            COLLECTION_COLUMNS, [collection.get_data() for collection in collections]
        )

    def remove_all(self, table_root: str, uuid_associate: str) -> None:
        return

    def remove_list(self, table_root: str, collections: Sequence[Collection]) -> None:
        collections = filter_default(collections)
        MANAGER_DATABASE.delete_entries(
            f"{table_root}collections", ("uuid",), [(collection.get_uuid(),) for collection in collections]
        )
        MANAGER_DATABASE.cursor.execute("VACUUM")


DB_COLLECTION = DB_Collection()
