from typing import Any, TypeVar, Callable
from ftplib import FTP
from PySide6.QtCore import QObject
from .manager_settings import MANAGER_SETTINGS
from .gui_classes import Function_Worker

T = TypeVar('T')


class FTP_Connection:
    def __init__(self) -> None:
        self.connection: FTP | None = None

    def refresh(self) -> None:
        address: str = MANAGER_SETTINGS["server_address"]
        username: str = MANAGER_SETTINGS["server_username"]
        password: str = MANAGER_SETTINGS["server_password"]
        if not address or not username:
            self.connection = None
            return
        if self.connection is not None:
            self.close()
        try:
            self.connection = FTP(address)
            self.connection.login(username, password)
        except:
            self.connection = None

    def refresh_threaded(self, parent: QObject | None, on_finish: Callable[[], None] | None = None) -> None:
        worker = Function_Worker(self.refresh, parent)
        if on_finish is not None:
            worker.finished.connect(on_finish)
        worker.start()

    def try_to_exectute(self, method: Callable[..., T], *args: Any) -> T | None:
        try:
            return method(*args)
        except ConnectionResetError:
            self.refresh()
            if self.connection is None:
                return None
            try:
                return method(*args)
            except ConnectionResetError:
                return None

    def check_connection(self) -> str | None:
        if self.connection is None:
            return None
        return self.try_to_exectute(self.connection.voidcmd, "NOOP")

    def nlst(self) -> list[str] | None:
        if self.connection is not None:
            return self.try_to_exectute(self.connection.nlst)
        return None

    def mkd(self, dirname: str) -> str | None:
        if self.connection is not None:
            return self.try_to_exectute(self.connection.mkd, dirname)
        return None

    def storbinary(self, cmd: str, fp: str) -> str | None:
        if self.connection is not None:
            return self.try_to_exectute(self.connection.storbinary, cmd, fp)
        return None

    def close(self) -> str | None:
        if self.connection is not None:
            return self.try_to_exectute(self.connection.close)
        return None


FTP_CONNECTION = FTP_Connection()
