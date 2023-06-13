from .class_tournament import Tournament
from .class_armageddon import Armageddon
from .functions_util import shorten_float
from .functions_tournament_knockout import get_uuids_in_current_level, get_end_rounds, update_participant_standings,\
    reverse_participant_standings
from .functions_tournament_util import get_standings_header_vertical
from .functions_categories import filter_list_by_category_range


def get_totals(games, games_per_tiebreak):
    return [games], [games_per_tiebreak]


def get_scores(score_1, score_2, score_dict):
    if score_1 == '-' == score_2:
        return [.5], [.5]
    else:
        return [score_dict[score_1]], [score_dict[score_2]]


class Tournament_Knockout(Tournament):
    def __init__(
            self, participants, name, shallow_particpant_count=None, parameters=None, variables=None, order=None,
            uuid=None, uuid_associate="00000000-0000-0000-0000-000000000002"
    ):
        super().__init__(
            participants, name, shallow_particpant_count, parameters, variables, order, uuid, uuid_associate
        )
        self.mode = "Knockout"
        self.parameters = parameters or {
            "games": 2,
            "games_per_tiebreak": 2,
            "armageddon": Armageddon()
        }
        self.parameter_display = {
            "games": "Games per Match",
            "games_per_tiebreak": "Games per Tiebreak",
            "armageddon": "Armageddon"
        }
        self.variables = variables or self.variables | {"participant_standings": None}

    def seat_participants(self):
        self.set_participants(sorted(
            self.get_participants(), key=lambda x: 0 if x.get_rating() is None else x.get_rating(), reverse=True
        ))

    @staticmethod
    def get_globals():
        return globals()

    def set_participants(self, participants):
        super().set_participants(participants)
        participant_uuids = self.get_participant_uuids()
        if len(participant_uuids) < 2 or self.get_round() > 1:
            return
        through = 2 * (1 << (len(participant_uuids).bit_length() - 1)) - len(participant_uuids)
        self.set_variable(
            "participant_standings",
            {
                uuid: {"level": 1 if i < through else 0, "score": [0], "beaten_by_seat": None, "seating": i+1}
                for i, uuid in enumerate(participant_uuids)
            }
        )

    def is_valid_parameters(self):
        return self.get_parameter("games") > 0 and self.get_parameter("games_per_tiebreak") > 0

    def is_done(self):
        return tuple(
            standing["beaten_by_seat"] for standing in self.get_variable("participant_standings").values()
        ).count(None) == 1

    def add_results(self, results):
        super().add_results(results)
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        for (uuid_1, score_1), (uuid_2, score_2) in self.get_results()[-1]:
            update_participant_standings(
                uuid_1, uuid_2, *get_scores(score_1, score_2, self.get_score_dict()),
                self.get_variable("participant_standings"), games, games_per_tiebreak, self.get_parameter("armageddon"),
                *get_totals(games, games_per_tiebreak)
            )

    def remove_results(self):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        for (uuid_1, score_1), (uuid_2, score_2) in self.get_results()[-1]:
            reverse_participant_standings(
                uuid_1, uuid_2, *get_scores(score_1, score_2, self.get_score_dict()),
                self.get_variable("participant_standings"), games, games_per_tiebreak, self.get_parameter("armageddon"),
                *get_totals(games, games_per_tiebreak)
            )
        super().remove_results()

    def get_round_name(self, r):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        end_rounds = get_end_rounds(
            self.get_variable("participant_standings"), games, games_per_tiebreak, armageddon,
            *get_totals(games, games_per_tiebreak)
        )

        counter = 1
        while len(end_rounds) > 0 and r > end_rounds[0]:
            r -= end_rounds.pop(0)
            counter += 1

        if armageddon.is_armageddon(games, games_per_tiebreak, r):
            return "Round", f" {counter}.A"
        if r <= games:
            if games == 1:
                return "Round", f" {counter}"
            return "Round", f" {counter}.{r}"
        return "Round", f" {counter}.T{r - games}"

    def get_standings(self, category_range=None):
        header_horizontal = ["Name", "Matches", "Match Points"]
        participant_standings = self.get_variable("participant_standings")
        participants = self.get_participants()
        if category_range is not None:
            participants = filter_list_by_category_range(participants, *category_range)

        table = sorted((
            (
                participant,
                participant_standings[participant.get_uuid()]["level"] - 1,
                shorten_float(participant_standings[participant.get_uuid()]["score"][0])
            ) for participant in participants
        ), key=lambda x: x[1:], reverse=True)

        header_vertical = get_standings_header_vertical(table)
        return header_horizontal, header_vertical, table

    def load_pairings(self):
        if self.get_pairings() is not None or self.is_done():
            return
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")

        uuids = sorted(
            get_uuids_in_current_level(participant_standings), key=lambda x: participant_standings[x]["seating"]
        )
        pairings = [(uuids[i], uuids[i + int(len(uuids) / 2)]) for i in range(int(len(uuids) / 2))]
        score_sum = participant_standings[pairings[0][0]]["score"][0] + \
            participant_standings[pairings[0][1]]["score"][0]

        if armageddon.is_armageddon(games, games_per_tiebreak, score_sum + 1):
            self.set_pairings([armageddon.determine_color(uuid_1, uuid_2) for uuid_1, uuid_2 in pairings])
        elif score_sum % 2:
            self.set_pairings([(uuid_2, uuid_1) for uuid_1, uuid_2 in pairings])
        else:
            self.set_pairings(pairings)
