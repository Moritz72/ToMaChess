from __future__ import annotations
from typing import Sequence
from .pairing_item import Pairing_Item


class Bracket_Tree_Node:
    def __init__(
            self, items: tuple[Pairing_Item | None, Pairing_Item | None],
            scores: list[tuple[str, str]], winner: bool | None = None
    ) -> None:
        self.items: tuple[Pairing_Item | None, Pairing_Item | None] = items
        self.scores: list[tuple[str, str]] = scores
        self.winner: bool | None = winner
        self.children: tuple[Bracket_Tree_Node | None, Bracket_Tree_Node | None] = (None, None)
        self.connections: tuple[bool, bool] = (False, False)

    def __repr__(self) -> str:
        return f"Node{self.items.__repr__()}"

    def set_children(self, children: Sequence[Bracket_Tree_Node], connections: Sequence[bool]) -> None:
        assert(len(children) < 3 and len(children) == len(connections))
        if len(children) == 0:
            return
        if len(children) == 1 and self.children[0] is None:
            self.children = (children[0], self.children[1])
            self.connections = (connections[0], self.connections[1])
        elif len(children) == 1:
            self.children = (self.children[0], children[0])
            self.connections = (self.connections[0], connections[0])
        else:
            self.children = (children[0], children[1])
            self.connections = (connections[0], connections[1])

    def get_depth(self) -> int:
        return max(0 if child is None else child.get_depth() for child in self.children) + 1

    def get_n_children(self) -> int:
        return 2 - self.children.count(None)

    def get_generations_with_siblings(self) -> list[bool]:
        child_sizes = [child.get_generations_with_siblings() for child in self.children if child is not None]
        max_len = max([len(child_size) for child_size in child_sizes] or [0])
        return [self.get_n_children() == 2] + [
            any(child_size[i] if i < len(child_size) else False for child_size in child_sizes) for i in range(max_len)
        ]

    def get_widths(self) -> list[int]:
        sibling_gens = self.get_generations_with_siblings()
        return [2 ** sum(sibling_gens[:i] or [False]) for i in range(len(sibling_gens))]

    def get_max_score_lengths(self) -> list[int]:
        child_max_len = [child.get_max_score_lengths() for child in self.children if child is not None] + [[0]]
        max_len = max([len(child_max_len) for child_max_len in child_max_len] or [0])
        return [len(self.scores)] + [
            max(child_size[i] if i < len(child_size) else 0 for child_size in child_max_len) for i in range(max_len)
        ]

    def swap(self) -> None:
        self.items = self.items[::-1]
        self.scores = [score[::-1] for score in self.scores]
        self.winner = self.winner if self.winner is None else not self.winner
        self.connections = self.connections[::-1]


class Bracket_Tree:
    def __init__(self, root: Bracket_Tree_Node) -> None:
        self.root: Bracket_Tree_Node = root

    def __repr__(self) -> str:
        return f"Tree({self.root.__repr__()})"
