from ..parameters.parameter import Parameter
from ...common.registry import Registry


class Parameter_Registry(Registry[Parameter]):
    pass


PARAMETER_REGISTRY = Parameter_Registry()
