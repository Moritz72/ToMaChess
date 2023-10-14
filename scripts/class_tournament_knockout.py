from .class_tournament import Tournament
from .class_armageddon import Armageddon
from .functions_pairing import PAIRING_FUNCTIONS
from .functions_util import shorten_float
from .functions_tournament_knockout import get_uuids_in_current_level, get_end_rounds, update_participant_standings,\
    reverse_participant_standings
from .functions_tournament_util import get_standings_header_vertical
from .functions_player import sort_players_by_rating
from .functions_categories import filter_list_by_category_range


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
        self.parameters = {
            "games": 2,
            "games_per_tiebreak": 2,
            "pairing_method": ["Slide", "Fold", "Adjacent", "Random", "Custom"],
            "armageddon": Armageddon()
        } | self.parameters
        self.parameter_display = {
            "games": "Games per Match",
            "games_per_tiebreak": "Games per Tiebreak",
            "pairing_method": "Pairing Method",
            "armageddon": "Armageddon"
        }
        self.variables = {"participant_standings": dict()} | self.variables

    @staticmethod
    def get_globals():
        return globals()

    def set_participants(self, participants):
        super().set_participants(sort_players_by_rating(participants))
        if "participant_standings" not in self.get_variables():
            self.set_variable("participant_standings", dict())
        participant_standings = self.get_variable("participant_standings")
        uuids = self.get_participant_uuids()
        for uuid in uuids:
            if uuid not in participant_standings:
                participant_standings[uuid] = {
                    "level": 0, "score": self.get_initial_score(),
                    "beaten_by_seat": None, "seating": len(participant_standings) + 1
                }

    def get_changeable_parameters(self, initial=False):
        if initial:
            return super().get_changeable_parameters(initial)
        return {}

    def is_valid_parameters(self):
        return self.get_parameter("games") > 0 and self.get_parameter("games_per_tiebreak") > 0

    def is_valid_pairings(self, results):
        uuids = [uuid_1 for (uuid_1, _), (_, _) in results] + [uuid_2 for (_, _), (uuid_2, _) in results]
        return len(uuids) == len(set(uuids))

    def is_done(self):
        return tuple(
            standing["beaten_by_seat"] for standing in self.get_variable("participant_standings").values()
        ).count(None) == 1

    @staticmethod
    def get_initial_score():
        return [0]

    def get_totals(self):
        return [self.get_parameter("games")], [self.get_parameter("games"), self.get_parameter("games_per_tiebreak")]

    def get_latest_scores(self):
        return [
            get_scores(score_1, score_2, self.get_score_dict())
            for (uuid_1, score_1), (uuid_2, score_2) in self.get_results()[-1]
        ]

    def add_results(self, results):
        super().add_results(results)
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")
        level = participant_standings[self.get_results()[-1][0][0][0]]["level"]
        uuids = set()

        for ((uuid_1, _), (uuid_2, _)), scores in zip(self.get_results()[-1], self.get_latest_scores()):
            update_participant_standings(
                uuid_1, uuid_2, *scores, participant_standings,
                games, games_per_tiebreak, armageddon, *self.get_totals()
            )
            uuids = uuids | {uuid_1, uuid_2}
        alives = set(uuid for uuid in participant_standings if participant_standings[uuid]["beaten_by_seat"] is None)
        for uuid in alives.difference(uuids):
            participant_standings[uuid]["level"] = level + 1

    def remove_results(self):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")
        uuids = set()

        for ((uuid_1, _), (uuid_2, _)), scores in zip(self.get_results()[-1], self.get_latest_scores()):
            reverse_participant_standings(
                uuid_1, uuid_2, *scores, participant_standings,
                games, games_per_tiebreak, armageddon, *self.get_totals()
            )
            uuids = uuids | {uuid_1, uuid_2}
        level = participant_standings[self.get_results()[-1][0][0][0]]["level"]
        alives = set(uuid for uuid in participant_standings if participant_standings[uuid]["beaten_by_seat"] is None)
        if all(participant_standings[uuid]["score"] == self.get_initial_score() for uuid in uuids):
            for uuid in alives:
                participant_standings[uuid]["level"] = level
        super().remove_results()

    def get_round_name(self, r):
        games, games_per_tiebreak = self.get_parameter("games"), self.get_parameter("games_per_tiebreak")
        armageddon = self.get_parameter("armageddon")
        participant_standings = self.get_variable("participant_standings")
        end_rounds = get_end_rounds(participant_standings, games, games_per_tiebreak, armageddon, *self.get_totals())

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
                participant_standings[participant.get_uuid()]["level"],
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

        uuids = get_uuids_in_current_level(participant_standings)
        score_sum = sum(participant_standings[uuid]["score"][0] for uuid in uuids) / len(uuids)
        pairing_method = self.get_parameter("pairing_method")[0]

        if score_sum == 0 and (len(uuids) & (len(uuids) - 1)):
            through = 2 * (1 << (len(uuids).bit_length() - 1)) - len(uuids)
            uuids = uuids[through:]

        if score_sum == 0 and pairing_method == "Custom":
            pairings = int(len(uuids) / 2) * [(uuids, uuids)]
        elif score_sum == 0:
            pairing_indices = PAIRING_FUNCTIONS[pairing_method](len(uuids))
            pairings = [(uuids[i_1], uuids[i_2]) for i_1, i_2 in pairing_indices]
        else:
            pairings = [(uuid_2, uuid_1) for (uuid_1, _), (uuid_2, _) in self.get_results()[-1] if uuid_1 in uuids]
            drop_outs = self.get_variable("drop_outs")
            for i, (uuid_1, uuid_2) in enumerate(pairings):
                if uuid_1 in drop_outs and uuid_2 in drop_outs:
                    pairings[i] = (None, None)
                    participant_standings[uuid_1]["beaten_by_seat"] = 0
                    participant_standings[uuid_2]["beaten_by_seat"] = 0
            while (None, None) in pairings:
                pairings.remove((None, None))

        if armageddon.is_armageddon(games, games_per_tiebreak, score_sum + 1):
            self.set_pairings([armageddon.determine_color(uuid_1, uuid_2) for uuid_1, uuid_2 in pairings])
        else:
            self.set_pairings(pairings)

    def drop_out_participants(self, uuids=[]):
        if self.get_participant_count(drop_outs=False) <= len(uuids) + 1:
            return False
        participant_standings = self.get_variable("participant_standings")
        uuids_current = get_uuids_in_current_level(participant_standings)
        score_sum = sum(participant_standings[uuid]["score"][0] for uuid in uuids_current) / len(uuids_current)

        if score_sum == 0:
            for uuid in uuids:
                if participant_standings[uuid]["beaten_by_seat"] is None:
                    participant_standings[uuid]["beaten_by_seat"] = 0
        return super().drop_out_participants(uuids)

    def drop_in_participants(self, participants=[]):
        participant_standings = self.get_variable("participant_standings")
        uuids = get_uuids_in_current_level(participant_standings)
        score_sum = sum(participant_standings[uuid]["score"][0] for uuid in uuids) / len(uuids)

        if score_sum > 0:
            return False
        participants_filtered = []
        next_seat = len(self.get_participants()) + 1
        for participant in participants:
            uuid = participant.get_uuid()
            if uuid in participant_standings:
                standing = participant_standings[uuid]
                if standing["beaten_by_seat"]:
                    continue
                standing["level"] = participant_standings[uuids[0]]["level"]
                standing["beaten_by_seat"] = None
                standing["score"] = self.get_initial_score()
            else:
                participant_standings[uuid] = {
                    "level": participant_standings[uuids[0]]["level"], "score": self.get_initial_score(),
                    "beaten_by_seat": None, "seating": next_seat
                }
                next_seat += 1
            participants_filtered.append(participant)

        return super().drop_in_participants(participants_filtered)
