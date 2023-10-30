from abc import abstractmethod


class Custom_Parameter:
    def __init__(self, **args):
        self.args = dict()
        self.args_display = dict()
        self.initialize_args_and_args_display(args)
        self.fill_in_default()
        self.window_update_necessary = False

    @abstractmethod
    def initialize_args_and_args_display(self, args):
        pass

    def get_dict(self):
        return {"args": self.args}

    @abstractmethod
    def fill_in_default(self):
        pass

    @abstractmethod
    def update(self, args):
        pass

    def get_args_and_args_display(self):
        return self.args, self.args_display

    @abstractmethod
    def is_valid(self):
        pass

    @abstractmethod
    def get_display_status(self):
        pass
