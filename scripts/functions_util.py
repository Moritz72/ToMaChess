import os
import os.path
from typing import Sequence, Any, TypeVar, cast
from codecs import open

T = TypeVar('T')


def read_file(path: str, encoding: str | None = "utf-8") -> str:
    with open(path, 'r', encoding) as file:
        return file.read()


def write_file(path: str, content: str, encoding: str | None = "utf-8") -> None:
    with open(path, 'w', encoding) as file:
        file.write(content)


def get_root_directory() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))


def get_app_data_directory() -> str:
    return os.path.join(cast(str, os.getenv("APPDATA")), "ToMaChess")


def get_version() -> str | None:
    readme = os.path.join(get_root_directory(), "README.txt")
    if not os.path.exists(readme):
        return None
    with open(readme) as file:
        first_line = file.readline().rstrip()
        if len(first_line) > 10 and first_line[:10] == "ToMaChess ":
            return first_line[10:]
        return None


def get_image(name: str) -> str:
    return os.path.join(get_root_directory(), "images", name)


def get_uuid_from_numbers(n_1: int, n_2: int = 0, n_3: int = 0) -> str:
    return f"00000000-0000-{str(n_3).zfill(4)}-{str(n_2).zfill(4)}-{str(n_1).zfill(12)}"


def make_app_data_folder() -> None:
    path = get_app_data_directory()
    if not os.path.exists(path):
        os.mkdir(path)


def remove_temporary_files() -> None:
    path = os.path.join(get_app_data_directory(), "temp")
    if not os.path.exists(path):
        os.mkdir(path)
    for file in os.listdir(path):
        os.remove(os.path.join(path, file))


def shorten_float(value: float) -> float:
    return int(value) if float(value).is_integer() else float(str(value).rstrip('0').rstrip('.'))


def has_duplicates(list_of_hashables: Sequence[Any]) -> bool:
    return len(set(list_of_hashables)) != len(list_of_hashables)


def remove_duplicates(list_of_hashables: Sequence[T]) -> list[T]:
    return list({hashable: None for hashable in list_of_hashables}.keys())
