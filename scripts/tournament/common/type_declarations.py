from typing import Any
from ...player.player import Player
from ...team.team import Team

Participant = Player | Team
Tournament_Data = tuple[str, str, int, str, str, str, str, str]
Tournament_Data_Loaded = tuple[str, str, int, dict[str, Any], dict[str, Any], list[str], str, str]
