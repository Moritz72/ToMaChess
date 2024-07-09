from ..variables.variable import Variable
from ...common.registry import Registry


class Variable_Registry(Registry[Variable]):
    pass


VARIABLE_REGISTRY = Variable_Registry()
