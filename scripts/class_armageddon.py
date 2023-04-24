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
    def __init__(self, args={}, args_display={}):
        self.args = args
        self.args_display = args_display
        if "enabled" not in self.args:
            self.args["enabled"] = False
        if "enabled" not in self.args_display:
            self.args_display["enabled"] = "With Armageddon"
        if self.args["enabled"]:
            if "after_rounds" not in self.args:
                self.args["after_rounds"] = 1
            if "after_rounds" not in self.args_display:
                self.args_display["after_rounds"] = "After Tiebreak Pair"

    def update(self, args):
        if args["enabled"] != self.args["enabled"]:
            if args["enabled"]:
                self.args["enabled"] = True
                self.args["after_rounds"] = 1
                self.args["determine_color"] = ["In Order", "Random", "Choice"]
                self.args_display["after_rounds"] = "After Tiebreak Pair"
                self.args_display["determine_color"] = "Color Determination"
            else:
                self.args = {"enabled": False}
                self.args_display = {"enabled": "With Armageddon"}
        else:
            self.args = args

    def get_args_and_args_display(self):
        return self.args, self.args_display

    def is_armageddon(self, games, roun):
        return self.args["enabled"] and roun-games-2*self.args["after_rounds"] >= 1

    def determine_color(self, participant_1, participant_2):
        if self.args["determine_color"][0] == "In Order":
            return determine_color_default(participant_1, participant_2)
        elif self.args["determine_color"][0] == "Random":
            return determine_color_random(participant_1, participant_2)
        elif self.args["determine_color"][0] == "Choice":
            return determine_color_choice(participant_1, participant_2)

    @staticmethod
    def is_valid():
        return True
