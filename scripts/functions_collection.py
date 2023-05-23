from .class_database_handler import database_handler
from .class_collection import Collection


def is_default(collection):
    return collection.get_name() == "Default"


def filter_default(collections):
    return tuple(collection for collection in collections if not is_default(collection))


def collection_exists(table_root, uuid):
    return database_handler.entry_exists(f"{table_root}collections", ("uuid",), (uuid,))


def load_collection(table_root, uuid):
    entry = database_handler.get_entries(f"{table_root}players", ("uuid",), (uuid,))[0]
    return Collection(*entry)


def load_collections(table_root, object_type):
    if object_type not in ("Players", "Tournaments", "Teams", "Multi-Stage Tournaments"):
        return
    entries = database_handler.get_entries(f"{table_root}collections", ("object_type",), (object_type,))
    return sorted((Collection(*entry) for entry in entries), key=lambda x: (not is_default(x), x.get_name()))


def load_collections_all(table_root):
    database_handler.cursor.execute(f"SELECT * FROM {table_root}collections")
    return [Collection(*entry) for entry in database_handler.cursor.fetchall()]


def load_collections_like(table_root, name, limit):
    entries = database_handler.get_entries_like(
        f"{table_root}collections", tuple(), tuple(), ("name",), (name,), ("object_type", "name"), (True, True), limit
    )
    return [Collection(*entry) for entry in entries]


def add_collection(table_root, collection):
    if is_default(collection):
        return
    database_handler.add_entry(f"{table_root}collections", ("name", "object_type", "uuid"), collection.get_data())


def add_collections(table_root, collections):
    collections = filter_default(collections)
    database_handler.add_entries(
        f"{table_root}collections", ("name", "object_type", "uuid"),
        tuple(collection.get_data() for collection in collections)
    )


def update_collection(table_root, collection):
    if is_default(collection):
        return
    database_handler.update_entry(
        f"{table_root}collections", ("uuid",), (collection.get_uuid(),),
        ("name", "object_type", "uuid"), collection.get_data()
    )


def update_collections(table_root, collections):
    collections = filter_default(collections)
    database_handler.update_entries(
        f"{table_root}collections", ("uuid",), tuple((collection.get_uuid(),) for collection in collections),
        ("name", "object_type", "uuid"), tuple(collection.get_data() for collection in collections)
    )


def remove_collection(table_root, collection):
    if is_default(collection):
        return
    database_handler.delete_entry(f"{table_root}collections", ("uuid",), (collection.get_uuid(),))
    database_handler.cursor.execute("VACUUM")


def remove_collections(table_root, collections):
    collections = filter_default(collections)
    database_handler.delete_entries(
        f"{table_root}collections", ("uuid",), tuple((collection.get_uuid(),) for collection in collections)
    )
    database_handler.cursor.execute("VACUUM")
