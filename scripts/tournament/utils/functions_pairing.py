from random import shuffle
from typing import Callable


def get_pairings_slide(n: int, first_seed_white: bool = True) -> list[tuple[int, int]]:
    pairings = [(i, i + n // 2) for i in range(n // 2)]
    for i in range(first_seed_white, len(pairings), 2):
        pairings[i] = (pairings[i][1], pairings[i][0])
    if bool(n % 2):
        pairings.append((n - 1, n))
    return pairings


def get_pairings_fold(n: int, first_seed_white: bool = True) -> list[tuple[int, int]]:
    pairings = [(i, n - i - 1 - (n % 2)) for i in range(n // 2)]
    for i in range(first_seed_white, len(pairings), 2):
        pairings[i] = (pairings[i][1], pairings[i][0])
    if bool(n % 2):
        pairings.append((n - 1, n))
    return pairings


def get_pairings_adjacent(n: int, first_seed_white: bool = True) -> list[tuple[int, int]]:
    pairings = [(i, i + 1) for i in range(0, n, 2)]
    for i in range(first_seed_white, len(pairings), 2):
        pairings[i] = (pairings[i][1], pairings[i][0])
    if pairings[-1][0] == n:
        pairings[-1] = (pairings[-1][1], pairings[-1][0])
    return pairings


def get_pairings_random(n: int, first_seed_white: bool = True) -> list[tuple[int, int]]:
    indices = [i for i in range(n)]
    shuffle(indices)
    pairings = []
    for i in range(0, n - (n % 2), 2):
        if indices[i + 1] == 0 and first_seed_white:
            pairings.append((indices[i + 1], indices[i]))
        elif indices[i + 1] != 0 and not first_seed_white:
            pairings.append((indices[i], indices[i + 1]))
        else:
            pairings.append((indices[i], indices[i + 1]))
    if bool(n % 2):
        pairings.append((indices[-1], n))
    return pairings


def get_pairings_cycle(n: int, i: int) -> list[tuple[int, int]]:
    bye = bool(n % 2)
    n += n % 2
    div, mod = divmod(i - 1, n - 1)
    pairings = [(n - 1, mod)]
    pairings.extend([((mod - j) % (n - 1), (mod + j) % (n - 1)) for j in range(1, n // 2)])
    for j in range(len(pairings)):
        if bool((div + j) % 2):
            pairings[j] = (pairings[j][1], pairings[j][0])
    if bool(mod % 2):
        pairings[0] = (pairings[0][1], pairings[0][0])
    if bye:
        pairings = pairings[1:]
    return pairings


def get_pairings_berger(n: int, i: int) -> list[tuple[int, int]]:
    bye = bool(n % 2)
    n += n % 2
    div, mod = divmod(i - 1, n - 1)
    if bool(mod % 2):
        sign = -1
        pivot = int((n + mod) / 2)
    else:
        sign = 1
        pivot = int(mod / 2)
    pairings = [(pivot, n - 1)]
    pairings.extend([((pivot + sign * j) % (n - 1), (pivot - sign * j) % (n - 1)) for j in range(1, n // 2)])
    if mod % 2 != div % 2:
        pairings = [(p_2, p_1) for p_1, p_2 in pairings]
    if bye:
        pairings = pairings[1:]
    return pairings


PAIRING_FUNCTIONS: dict[str, Callable[[int, bool], list[tuple[int, int]]]] = {
    "Slide": get_pairings_slide,
    "Fold": get_pairings_fold,
    "Adjacent": get_pairings_adjacent,
    "Random": get_pairings_random,
}
PAIRING_FUNCTIONS_ROUND_ROBIN: dict[str, Callable[[int, int], list[tuple[int, int]]]] = {
    "Cycle": get_pairings_cycle,
    "Berger": get_pairings_berger
}
