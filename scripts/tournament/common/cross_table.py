from math import ceil, sqrt


def get_line_breaked_entry(entry: str | None) -> str | None:
    if entry is None:
        return None
    if len(entry) == 0:
        return ""
    interval = ceil(sqrt(len(entry)))
    return '\n'.join([entry[i:i + interval] for i in range(0, len(entry), interval)])


class Cross_Table(list[list[str | None]]):
    def __init__(
            self, table: list[list[str | None]], names_left: list[str] | None = None, names_top: list[str] | None = None
    ) -> None:
        super().__init__([[get_line_breaked_entry(entry) for entry in row] for row in table])
        self.names_left: list[str] | None = names_left
        self.names_top: list[str] | None = names_top

    def get_max_length(self) -> int:
        no_nones_list = [entry for row in self for entry in row if entry is not None]
        return max(entry.index('\n') if '\n' in entry else len(entry) for entry in no_nones_list)
