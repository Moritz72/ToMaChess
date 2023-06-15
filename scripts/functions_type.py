from .functions_collection import *
from .functions_ms_tournament import *
from .functions_player import *
from .functions_team import *
from .functions_tournament import *

TYPE_TO_MODES = {"player": MODES, "team": MODES_TEAM}
TYPE_TO_MODE_DEFAULT = {"player": MODE_DEFAULT, "team": MODE_DEFAULT_TEAM}
TYPE_TO_ADD_PARTICIPANT_WINDOW_ARGS = {"player": ("Add Players", "Players"), "team": ("Add Teams", "Teams")}


def get_function(object_type, action, multiple=False, shallow=False, specification=None):
    function_name = f"{action}_{object_type}"
    if multiple:
        function_name += 's'
    if shallow:
        function_name_shallow = f"{function_name}_shallow"
        if specification is not None:
            function_name_shallow += f"_{specification}"
        if function_name_shallow in globals():
            return globals()[function_name_shallow]
    if specification:
        function_name += f"_{specification}"
    if function_name in globals():
        return globals()[function_name]
