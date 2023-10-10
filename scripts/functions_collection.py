from .class_database_handler import DATABASE_HANDLER
from .class_collection import Collection

COLLECTION_ATTRIBUTE_LIST = ["Name", "Type"]


def is_default(collection):
    return collection.get_name() == "Default"


def sort_collections(collections):
    return sorted(collections, key=lambda x: (not is_default(x), x.get_name()))


def filter_default(collections):
    return tuple(collection for collection in collections if not is_default(collection))


def collection_exists(table_root, uuid):
    return DATABASE_HANDLER.entry_exists(f"{table_root}collections", ("uuid",), (uuid,))


def load_collection(table_root, uuid):
    entry = DATABASE_HANDLER.get_entries(f"{table_root}players", ("uuid",), (uuid,))[0]
    return Collection(*entry)


def load_collections(table_root, object_type):
    if object_type not in ("Players", "Tournaments", "Teams", "Multi-Stage Tournaments"):
        return
    entries = DATABASE_HANDLER.get_entries(f"{table_root}collections", ("object_type",), (object_type,))
    return sort_collections([Collection(*entry) for entry in entries])


def load_collections_all(table_root):
    DATABASE_HANDLER.cursor.execute(f"SELECT * FROM {table_root}collections")
    return sort_collections([Collection(*entry) for entry in DATABASE_HANDLER.cursor.fetchall()])


def load_collections_like(table_root, name, limit):
    entries = DATABASE_HANDLER.get_entries_like(
        f"{table_root}collections", tuple(), tuple(), ("name",), (name,), ("object_type", "name"), (True, True), limit
    )
    return sort_collections([Collection(*entry) for entry in entries])


def add_collection(table_root, collection):
    if is_default(collection):
        return
    DATABASE_HANDLER.add_entry(f"{table_root}collections", ("name", "object_type", "uuid"), collection.get_data())


def add_collections(table_root, collections):
    collections = filter_default(collections)
    DATABASE_HANDLER.add_entries(
        f"{table_root}collections", ("name", "object_type", "uuid"),
        tuple(collection.get_data() for collection in collections)
    )


def update_collection(table_root, collection):
    if is_default(collection):
        return
    DATABASE_HANDLER.update_entry(
        f"{table_root}collections", ("uuid",), (collection.get_uuid(),),
        ("name", "object_type", "uuid"), collection.get_data()
    )


def update_collections(table_root, collections):
    collections = filter_default(collections)
    DATABASE_HANDLER.update_entries(
        f"{table_root}collections", ("uuid",), tuple((collection.get_uuid(),) for collection in collections),
        ("name", "object_type", "uuid"), tuple(collection.get_data() for collection in collections)
    )


def remove_collection(table_root, collection):
    if is_default(collection):
        return
    DATABASE_HANDLER.delete_entry(f"{table_root}collections", ("uuid",), (collection.get_uuid(),))
    DATABASE_HANDLER.cursor.execute("VACUUM")


def remove_collections(table_root, collections):
    collections = filter_default(collections)
    DATABASE_HANDLER.delete_entries(
        f"{table_root}collections", ("uuid",), tuple((collection.get_uuid(),) for collection in collections)
    )
    DATABASE_HANDLER.cursor.execute("VACUUM")
