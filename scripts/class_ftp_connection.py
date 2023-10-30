from ftplib import FTP
from .class_settings_handler import SETTINGS_HANDLER
from .functions_gui import Function_Worker


class FTP_Connection:
    def __init__(self):
        self.connection = None

    def refresh(self):
        address = SETTINGS_HANDLER.get("server_address")
        username = SETTINGS_HANDLER.get("server_username")
        password = SETTINGS_HANDLER.get("server_password")
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

    def refresh_threaded(self, parent, on_finish=None):
        worker = Function_Worker(self.refresh, parent)
        if on_finish is not None:
            worker.finished.connect(on_finish)
        worker.start()

    def try_to_exectute(self, method, *args):
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

    def check_connection(self):
        if self.connection is None:
            return None
        return self.try_to_exectute(self.connection.voidcmd, "NOOP")

    def nlst(self):
        if self.connection is not None:
            return self.try_to_exectute(self.connection.nlst)

    def mkd(self, dirname):
        if self.connection is not None:
            return self.try_to_exectute(self.connection.mkd, dirname)

    def storbinary(self, cmd, fp):
        if self.connection is not None:
            return self.try_to_exectute(self.connection.storbinary, cmd, fp)

    def close(self):
        if self.connection is not None:
            return self.try_to_exectute(self.connection.close)


FTP_CONNECTION = FTP_Connection()
