from random import random
from .class_custom_parameter import Custom_Parameter


def determine_color_default(participant_1, participant_2):
    return participant_1, participant_2


def determine_color_random(participant_1, participant_2):
    if random() < .5:
        return participant_1, participant_2
    return participant_2, participant_1


def determine_color_choice(participant_1, participant_2):
    return [participant_1, participant_2], [participant_1, participant_2]


class Armageddon(Custom_Parameter):
    def initialize_args_and_args_display(self, args):
        if "args" in args:
            self.args = args["args"]
        if "enabled" not in self.args:
            self.args["enabled"] = False
        self.args_display = {"enabled": "With Armageddon"}

    def fill_in_default(self):
        if self.args["enabled"]:
            for key, value in zip(("after_rounds", "determine_color"), (1, ["In Order", "Random", "Choice"])):
                if key not in self.args:
                    self.args[key] = value
            self.args_display["after_rounds"] = "After Tiebreak"
            self.args_display["determine_color"] = "Color Determination"
        else:
            self.args = {"enabled": False}
            self.args_display = {"enabled": "With Armageddon"}

    def update(self, args):
        if args["enabled"] != self.args["enabled"]:
            self.args = {"enabled": args["enabled"]}
            self.fill_in_default()
            self.window_update_necessary = True
        else:
            self.args = args
            self.window_update_necessary = False

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

    def is_valid(self):
        return True
