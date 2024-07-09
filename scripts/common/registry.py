from typing import Callable, Type, TypeVar

T = TypeVar('T')


class Registry(dict[str, Type[T]]):
    def __init__(self):
        super().__init__()

    def register(self, key: str) -> Callable[[Type[T]], Type[T]]:
        def decorator(cls: Type[T]) -> Type[T]:
            self[key] = cls
            return cls
        return decorator
