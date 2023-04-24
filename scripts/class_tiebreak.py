from .functions_tiebreak import get_buchholz, get_buchholz_sum, get_sonneborn_berger, get_blacks,\
    get_number_of_wins, get_opponent_average_rating, get_cumulative_score, get_number_of_black_wins,\
    get_direct_encounter

tiebreaks = {
    "None": None,
    "Buchholz": get_buchholz,
    "Buchholz Sum": get_buchholz_sum,
    "Sonneborn-Berger": get_sonneborn_berger,
    "Games as Black": get_blacks,
    "Wins": get_number_of_wins,
    "Wins as Black": get_number_of_black_wins,
    "Average Rating": get_opponent_average_rating,
    "Cumulative Points": get_cumulative_score,
    "Direct Encounter": get_direct_encounter
}
abbreviations = {
    "None": None,
    "Buchholz": "BuHo",
    "Buchholz Sum": "BuSu",
    "Sonneborn-Berger": "SoBe",
    "Games as Black": "BlaG",
    "Wins": "Wins",
    "Wins as Black": "BlaW",
    "Average Rating": "AvRa",
    "Cumulative Points": "Cumu",
    "Direct Encounter": "DiEn"
}
func_args = {
    "None": {},
    "Buchholz": {"cut_down": 0, "cut_up": 0, "virtual": True},
    "Buchholz Sum": {"cut_down": 0, "cut_up": 0, "virtual": True},
    "Sonneborn-Berger": {"cut_down": 0, "cut_up": 0, "virtual": False},
    "Games as Black": {},
    "Wins": {"include_forfeits": False},
    "Wins as Black": {},
    "Average Rating": {"cut_down": 0, "cut_up": 0},
    "Cumulative Points": {"cut_down": 0, "cut_up": 0},
    "Direct Encounter": {}
}
func_args_display = {
    "None": {},
    "Buchholz": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual opponents"},
    "Buchholz Sum": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual opponents"},
    "Sonneborn-Berger": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)", "virtual": "Virtual opponents"},
    "Games as Black": {},
    "Wins": {"include_forfeits": "Include Forfeits"},
    "Wins as Black": {},
    "Average Rating": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Cumulative Points": {"cut_down": "Cut (bottom)", "cut_up": "Cut (top)"},
    "Direct Encounter": {}
}


class Tiebreak:
    def __init__(self, args={}, args_display={}):
        self.args = args
        self.args_display = args_display
        if "functions" not in self.args:
            self.args["functions"] = "Buchholz"
        if "functions" not in self.args_display:
            self.args_display["functions"] = "Criterium"
        self.fill_in_default()

    def fill_in_default(self):
        for key, value in func_args[self.args["functions"][0]].items():
            if key not in self.args:
                self.args[key] = value
        for key, value in func_args_display[self.args["functions"][0]].items():
            if key not in self.args_display:
                self.args_display[key] = value

    def update(self, args):
        if args["functions"][0] != self.args["functions"][0]:
            self.args = {"functions": args["functions"]}
            self.args_display = {"functions": "Criterium"}
            self.fill_in_default()
        else:
            self.args = args

    def get_args_and_args_display(self):
        return self.args, self.args_display

    @staticmethod
    def is_valid():
        return True

    def evaluate(self, uuids, results, score_dict, player_all):
        func_args = self.args.copy()
        func = func_args.pop("functions")[0]
        return tiebreaks[func](uuids, results, score_dict, player_all, **func_args)

    def get_abbreviation(self):
        return abbreviations[self.args["functions"][0]]
