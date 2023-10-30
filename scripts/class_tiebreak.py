from inspect import getfullargspec
from .class_custom_parameter import Custom_Parameter
from .functions_tiebreak import get_buchholz, get_buchholz_sum, get_sonneborn_berger, get_blacks,\
    get_number_of_wins, get_opponent_average_rating, get_cumulative_score, get_number_of_black_wins,\
    get_direct_encounter, get_board_points, get_berliner_wertung

TIEBREAK_LIST = [
    "None", "Buchholz", "Buchholz Sum", "Sonneborn-Berger", "Games as Black", "Wins", "Wins as Black",
    "Average Rating", "Cumulative Score", "Direct Encounter"
]
TIEBREAK_LIST_TEAM = [
    "None", "Board Points", "Berliner Wertung", "Buchholz", "Buchholz Sum", "Sonneborn-Berger", "Wins",
    "Cumulative Score", "Direct Encounter"
]

TIEBREAKS = {
    "None": None,
    "Buchholz": get_buchholz,
    "Buchholz Sum": get_buchholz_sum,
    "Sonneborn-Berger": get_sonneborn_berger,
    "Games as Black": get_blacks,
    "Wins": get_number_of_wins,
    "Wins as Black": get_number_of_black_wins,
    "Average Rating": get_opponent_average_rating,
    "Cumulative Score": get_cumulative_score,
    "Direct Encounter": get_direct_encounter,
    "Board Points": get_board_points,
    "Berliner Wertung": get_berliner_wertung
}
FUNC_ARGS = {
    "None": {},
    "Buchholz": {"cut_down": 0, "cut_up": 0, "virtual": True},
    "Buchholz Sum": {"cut_down": 0, "cut_up": 0, "virtual": True},
    "Sonneborn-Berger": {"cut_down": 0, "cut_up": 0, "virtual": False},
    "Games as Black": {},
    "Wins": {"include_forfeits": False},
    "Wins as Black": {},
    "Average Rating": {"cut_down": 0, "cut_up": 0},
    "Cumulative Score": {"cut_down": 0, "cut_up": 0},
    "Direct Encounter": {},
    "Board Points": {},
    "Berliner Wertung": {}
}
FUNC_ARGS_DISPLAY = {
    "None": {},
    "Buchholz": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Buchholz Sum": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Sonneborn-Berger": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual Opponents"},
    "Games as Black": {},
    "Wins": {"include_forfeits": "Include Forfeits"},
    "Wins as Black": {},
    "Average Rating": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Cumulative Score": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Direct Encounter": {},
    "Board Points": {},
    "Berliner Wertung": {}
}


def get_tiebreak_list(default, team=False):
    if team:
        return sorted(TIEBREAK_LIST_TEAM, key=lambda x: x != default)
    return sorted(TIEBREAK_LIST, key=lambda x: x != default)


class Tiebreak(Custom_Parameter):
    def initialize_args_and_args_display(self, args):
        if "args" in args:
            self.args = args["args"]
        if "functions" not in self.args:
            self.args["functions"] = get_tiebreak_list("None")
        self.args_display = {"functions": "Criterion"}

    def fill_in_default(self):
        for key, value in FUNC_ARGS[self.args["functions"][0]].items():
            if key not in self.args:
                self.args[key] = value
        for key, value in FUNC_ARGS_DISPLAY[self.args["functions"][0]].items():
            if key not in self.args_display:
                self.args_display[key] = value

    def update(self, args):
        if args["functions"][0] != self.args["functions"][0]:
            self.args = {"functions": args["functions"]}
            self.args_display = {"functions": "Criterium"}
            self.fill_in_default()
            self.window_update_necessary = True
        else:
            self.args = args
            self.window_update_necessary = False

    def is_valid(self):
        return True

    def evaluate(self, args):
        func_args = self.args.copy() | args
        func = TIEBREAKS[func_args.pop("functions")[0]]
        return func(**{key: value for key, value in func_args.items() if key in getfullargspec(func).args})

    def get_display_status(self):
        return self.args["functions"][0]
