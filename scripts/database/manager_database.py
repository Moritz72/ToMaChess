import os
import os.path
from typing import Sequence, Any
from sqlite3 import connect
from ..common.functions_util import get_app_data_directory, get_root_directory, read_file


class Manager_Database:
    def __init__(self) -> None:
        data_path = os.path.join(get_app_data_directory(), "data")
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        self.conn = connect(os.path.join(data_path, "database.db"), check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", ("collections",))
        if self.cursor.fetchone():
            return
        self.cursor.executescript(read_file(os.path.join(get_root_directory(), "sql", "create_tables.sql")))
        self.cursor.executescript(read_file(os.path.join(get_root_directory(), "sql", "add_collections.sql")))
        self.conn.commit()

    def add_entries(self, table: str, column_names: Sequence[str], column_values_list: Sequence[Sequence[Any]]) -> None:
        if not bool(column_values_list):
            return
        query = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        self.cursor.executemany(query, column_values_list)
        self.conn.commit()

    def update_entries(
            self, table: str, search_column_names: Sequence[str], search_column_values_list: Sequence[Sequence[Any]],
            enter_column_names: Sequence[str], enter_column_values_list: Sequence[Sequence[Any]]
    ) -> None:
        if not bool(search_column_values_list) or not bool(enter_column_values_list):
            return
        query = (
            f"UPDATE {table} SET {', '.join((column_name + ' = ?' for column_name in enter_column_names))} "
            f"WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        parameters = tuple(
            list(enter_column_values) + list(search_column_values)
            for search_column_values, enter_column_values in zip(search_column_values_list, enter_column_values_list)
        )
        self.cursor.executemany(query, parameters)
        self.conn.commit()

    def delete_entry(
            self, table: str, search_column_names: Sequence[str], search_column_values: Sequence[Any]
    ) -> None:
        query = f"DELETE FROM {table} WHERE {' AND '.join([name + ' = ?' for name in search_column_names])}"
        self.cursor.execute(query, search_column_values)
        self.conn.commit()

    def delete_entries(
            self, table: str, search_column_names: Sequence[str], search_column_values_list: Sequence[Sequence[Any]]
    ) -> None:
        if not bool(search_column_values_list):
            return
        query = f"DELETE FROM {table} WHERE {' AND '.join([name + ' = ?' for name in search_column_names])}"
        self.cursor.executemany(query, search_column_values_list)
        self.conn.commit()

    def get_entries(
            self, table: str, search_column_names: Sequence[str], search_column_values: Sequence[Any]
    ) -> list[tuple[Any, ...]]:
        query = f"SELECT * FROM {table} WHERE {' AND '.join([name + ' = ?' for name in search_column_names])}"
        self.cursor.execute(query, search_column_values)
        return self.cursor.fetchall()

    def get_entries_list(
            self, table: str, search_column_names: Sequence[str], search_column_lists: Sequence[Sequence[Any]]
    ) -> list[tuple[Any, ...]]:
        if not bool(search_column_lists) or not bool(search_column_lists[0]):
            return []
        query_parts = [
            f"{name} IN ({','.join('?' * len(values))})"
            for name, values in zip(search_column_names, search_column_lists)
        ]
        query = f"SELECT * FROM {table} WHERE {' AND '.join(query_parts)}"
        self.cursor.execute(query, tuple(element for column_list in search_column_lists for element in column_list))
        return self.cursor.fetchall()

    def get_entries_like(
            self, table: str, search_column_names: Sequence[str], search_column_values: Sequence[Any],
            like_column_names: Sequence[str], like_column_values: Sequence[Any],
            order_column_names: Sequence[str] = tuple(), order_column_ascs: Sequence[Any] = tuple(),
            limit: int | None = None
    ) -> list[tuple[Any, ...]]:
        query = f"SELECT * FROM {table} WHERE {' AND '.join([name + ' LIKE ?' for name in like_column_names])}"
        if bool(search_column_names):
            query += f" AND {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        if order_column_names:
            query += " ORDER BY " + ", ".join(
                f"{name} {'ASC' if asc else 'DESC'}" for name, asc in zip(order_column_names, order_column_ascs)
            )
        if limit is not None:
            query += f" LIMIT {limit}"
        self.cursor.execute(query, [f"%{value}%" for value in like_column_values] + list(search_column_values))
        return self.cursor.fetchall()

    def entry_exists(self, table: str, search_column_names: Sequence[str], search_column_values: Sequence[Any]) -> bool:
        query = f"SELECT COUNT(*) FROM {table} WHERE {' AND '.join([name + ' = ?' for name in search_column_names])}"
        self.cursor.execute(query, search_column_values)
        return bool(self.cursor.fetchone()[0] > 0)


MANAGER_DATABASE = Manager_Database()
