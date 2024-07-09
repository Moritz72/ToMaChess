from ..tournaments.tournament import Tournament
from ...common.registry import Registry


class Tournament_Registry(Registry[Tournament]):
    def get_modes(self) -> list[str]:
        return sorted(self.keys())

    @staticmethod
    def get_mode_default() -> str:
        return "Swiss"


class Team_Tournament_Registry(Tournament_Registry):
    @staticmethod
    def get_mode_default() -> str:
        return "Swiss (Team)"


TOURNAMENT_REGISTRY = Tournament_Registry()
TEAM_TOURNAMENT_REGISTRY = Team_Tournament_Registry()
