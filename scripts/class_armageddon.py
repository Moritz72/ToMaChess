from random import random


def determine_color_default(participant_1, participant_2):
    return participant_1, participant_2


def determine_color_random(participant_1, participant_2):
    if random() < .5:
        return participant_1, participant_2
    return participant_2, participant_1


def determine_color_choice(participant_1, participant_2):
    return [participant_1, participant_2], [participant_1, participant_2]


class Armageddon:
    def __init__(self, args=None, args_display=None):
        self.args = args or {}
        self.args_display = args_display or {}
        if "enabled" not in self.args:
            self.args["enabled"] = False
        if "enabled" not in self.args_display:
            self.args_display["enabled"] = "With Armageddon"
        if self.args["enabled"]:
            if "after_rounds" not in self.args:
                self.args["after_rounds"] = 1
            if "after_rounds" not in self.args_display:
                self.args_display["after_rounds"] = "After Tiebreak"

    def update(self, args):
        if args["enabled"] != self.args["enabled"]:
            if args["enabled"]:
                self.args["enabled"] = True
                self.args["after_rounds"] = 1
                self.args["determine_color"] = ["In Order", "Random", "Choice"]
                self.args_display["after_rounds"] = "After Tiebreak"
                self.args_display["determine_color"] = "Color Determination"
            else:
                self.args = {"enabled": False}
                self.args_display = {"enabled": "With Armageddon"}
        else:
            self.args = args

    def get_args_and_args_display(self):
        return self.args, self.args_display

    def is_armageddon(self, games, games_per_tiebreak, roun):
        return self.args["enabled"] and roun - games - games_per_tiebreak * self.args["after_rounds"] >= 1

    def determine_color(self, participant_1, participant_2):
        match self.args["determine_color"][0]:
            case "In Order":
                return determine_color_default(participant_1, participant_2)
            case "Random":
                return determine_color_random(participant_1, participant_2)
            case "Choice":
                return determine_color_choice(participant_1, participant_2)

    @staticmethod
    def is_valid():
        return True
