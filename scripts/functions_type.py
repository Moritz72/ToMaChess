from .functions_collection import *
from .functions_ms_tournament import *
from .functions_player import *
from .functions_team import *
from .functions_tournament import *

type_to_modes = {"player": modes, "team": modes_team}
type_to_mode_default = {"player": mode_default, "team": mode_default_team}
type_to_add_participant_window_args = {"player": ("Add Players", "Players"), "team": ("Add Teams", "Teams")}


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
