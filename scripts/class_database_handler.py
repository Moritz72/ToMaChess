import os
import os.path
from sqlite3 import connect
from .functions_util import get_root_directory


class Database_Handler:
    def __init__(self):
        data_path = os.path.join(get_root_directory(), "data")
        if not os.path.exists(data_path):
            os.mkdir(data_path)
        self.conn = connect(os.path.join(data_path, "database.db"), check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def add_entry(self, table, column_names, column_values):
        query = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        self.cursor.execute(query, column_values)
        self.conn.commit()

    def add_entries(self, table, column_names, column_values_list):
        if not list(column_values_list):
            return
        query = f"INSERT INTO {table} ({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        self.cursor.executemany(query, column_values_list)
        self.conn.commit()

    def add_or_update_entry(self, table, column_names, column_values):
        self.conn.execute("PRAGMA foreign_keys = OFF;")
        query = (
            f"INSERT OR REPLACE INTO {table} "
            f"({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        )
        self.cursor.execute(query, column_values)
        self.conn.commit()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def add_or_update_entries(self, table, column_names, column_values_list):
        if not list(column_values_list):
            return
        self.conn.execute("PRAGMA foreign_keys = OFF;")
        query = (
            f"INSERT OR REPLACE INTO {table} "
            f"({', '.join(column_names)}) VALUES ({', '.join(['?'] * len(column_names))})"
        )
        self.cursor.executemany(query, column_values_list)
        self.conn.commit()
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def update_entry(self, table, search_column_names, search_column_values, enter_column_names, enter_column_values):
        query = (
            f"UPDATE {table} SET {', '.join((column_name + ' = ?' for column_name in enter_column_names))} "
            f"WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.execute(query, list(enter_column_values) + list(search_column_values))
        self.conn.commit()

    def update_entries(
            self, table, search_column_names, search_column_values_list, enter_column_names, enter_column_values_list
    ):
        if not search_column_values_list or not enter_column_values_list:
            return
        query = (
            f"UPDATE {table} SET {', '.join((column_name + ' = ?' for column_name in enter_column_names))} "
            f"WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.executemany(
            query,
            tuple(
                list(enter_column_values)+list(search_column_values)
                for search_column_values, enter_column_values
                in zip(search_column_values_list, enter_column_values_list)
            )
        )
        self.conn.commit()

    def delete_entry(self, table, search_column_names, search_column_values):
        query = (
            f"DELETE FROM {table} WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.execute(query, search_column_values)
        self.conn.commit()

    def delete_entries(self, table, search_column_names, search_column_values_list):
        if not list(search_column_values_list):
            return
        query = (
            f"DELETE FROM {table} WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.executemany(query, search_column_values_list)
        self.conn.commit()

    def delete_entries_list(self, table, search_column_names, search_column_lists):
        if not search_column_lists or not search_column_lists[0]:
            return tuple()
        query_parts = [
            f"{column_name} IN ({','.join('?' * len(column_list))})"
            for column_name, column_list in zip(search_column_names, search_column_lists)
        ]
        query = f"DELETE FROM {table} WHERE {' AND '.join(query_parts)}"
        self.cursor.execute(query, tuple(element for column_list in search_column_lists for element in column_list))

    def get_entries(self, table, search_column_names, search_column_values):
        query = (
            f"SELECT * FROM {table} "
            f"WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.execute(query, search_column_values)
        return self.cursor.fetchall()

    def get_entries_list(self, table, search_column_names, search_column_lists):
        if not search_column_lists or not search_column_lists[0]:
            return tuple()
        query_parts = [
            f"{column_name} IN ({','.join('?' * len(column_list))})"
            for column_name, column_list in zip(search_column_names, search_column_lists)
        ]
        query = f"SELECT * FROM {table} WHERE {' AND '.join(query_parts)}"
        self.cursor.execute(query, tuple(element for column_list in search_column_lists for element in column_list))
        return self.cursor.fetchall()

    def get_entries_like(
            self, table, search_column_names, search_column_values, like_column_names, like_column_values,
            order_column_names=[], order_column_ascs=[], limit=None
    ):
        query = (
            f"SELECT * FROM {table} "
            f"WHERE {' AND '.join([column_name + ' LIKE ?' for column_name in like_column_names])}"
        )
        if search_column_names:
            query += f" AND {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        if order_column_names:
            query_part = ", ".join(
                f"{column_name} {'ASC' if column_asc else 'DESC'}"
                for column_name, column_asc in zip(order_column_names, order_column_ascs)
            )
            query += f" ORDER BY {query_part}"
        if limit:
            query += f" LIMIT {limit}"
        self.cursor.execute(query, [f"%{value}%" for value in like_column_values]+list(search_column_values))
        return self.cursor.fetchall()

    def entry_exists(self, table, search_column_names, search_column_values):
        query = (
            f"SELECT COUNT(*) FROM {table} "
            f"WHERE {' AND '.join([column_name + ' = ?' for column_name in search_column_names])}"
        )
        self.cursor.execute(query, search_column_values)
        result = self.cursor.fetchone()
        return result[0] > 0

    def create_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?", ("collections",))
        if self.cursor.fetchone():
            return
        self.cursor.execute("""
        CREATE TABLE collections
        (
            name TEXT, object_type TEXT, uuid TEXT PRIMARY KEY
        )
        """)
        self.cursor.execute("""
        CREATE TABLE players
        (
            name TEXT, sex TEXT, birthday TEXT, country TEXT, title TEXT, rating INTEGER, uuid TEXT,
            uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE tournaments
        (
            mode TEXT, name TEXT, participants INTEGER, parameters TEXT, variables TEXT, participant_order TEXT,
            uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE teams
        (
            name TEXT, members INTEGER, uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE ms_tournaments
        (
            name TEXT, participants INTEGER, stages_advance_lists TEXT, draw_lots INTEGER, stage INTEGER,
            tournament_order TEXT, uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES collections(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE players_to_teams
        (
            uuid_player TEXT, uuid_associate_player TEXT, uuid_team TEXT, uuid_associate_team TEXT,
            member_order INTEGER,
            FOREIGN KEY (uuid_player, uuid_associate_player) REFERENCES players(uuid, uuid_associate) ON DELETE CASCADE,
            FOREIGN KEY (uuid_team, uuid_associate_team) REFERENCES teams(uuid, uuid_associate) ON DELETE CASCADE,
            PRIMARY KEY (uuid_player, uuid_team)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE tournaments_players
        (
            name TEXT, sex TEXT, birthday TEXT, country TEXT, title TEXT, rating INTEGER, uuid TEXT,
            uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES tournaments(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE tournaments_teams
        (
            name TEXT, members INTEGER, uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES tournaments(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE tournaments_players_to_teams
        (
            uuid_player TEXT, uuid_associate_player TEXT, uuid_team TEXT, uuid_associate_team TEXT,
            member_order INTEGER,
            FOREIGN KEY (uuid_player, uuid_associate_player)
            REFERENCES tournaments_players(uuid, uuid_associate) ON DELETE CASCADE,
            FOREIGN KEY (uuid_team, uuid_associate_team)
            REFERENCES tournaments_teams(uuid, uuid_associate) ON DELETE CASCADE,
            PRIMARY KEY (uuid_player, uuid_associate_player, uuid_team, uuid_associate_team)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE ms_tournaments_tournaments
        (
            mode TEXT, name TEXT, participants INTEGER, parameters TEXT, variables TEXT, participant_order TEXT,
            uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE ms_tournaments_players
        (
            name TEXT, sex TEXT, birthday TEXT, country TEXT, title TEXT, rating INTEGER, uuid TEXT,
            uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE ms_tournaments_teams
        (
            name TEXT, members INTEGER, uuid TEXT, uuid_associate TEXT,
            FOREIGN KEY (uuid_associate) REFERENCES ms_tournaments(uuid) ON DELETE CASCADE,
            PRIMARY KEY (uuid, uuid_associate)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE ms_tournaments_players_to_teams
        (
            uuid_player TEXT, uuid_associate_player TEXT, uuid_team TEXT, uuid_associate_team TEXT,
            member_order INTEGER,
            FOREIGN KEY (uuid_player, uuid_associate_player)
            REFERENCES ms_tournaments_players(uuid, uuid_associate) ON DELETE CASCADE,
            FOREIGN KEY (uuid_team, uuid_associate_team)
            REFERENCES ms_tournaments_teams(uuid, uuid_associate) ON DELETE CASCADE,
            PRIMARY KEY (uuid_player, uuid_associate_player, uuid_team, uuid_associate_team)
        )
        """)
        self.add_entries(
            "collections", ("name", "object_type", "uuid"),
            (
                ("Default", "Players", "00000000-0000-0000-0000-000000000000"),
                ("Default", "Teams", "00000000-0000-0000-0000-000000000001"),
                ("Default", "Tournaments", "00000000-0000-0000-0000-000000000002"),
                ("Default", "Multi-Stage Tournaments", "00000000-0000-0000-0000-000000000003")
            )
        )


DATABASE_HANDLER = Database_Handler()
