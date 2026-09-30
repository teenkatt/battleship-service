import random

from battleship.placement import around, to_coordinate, to_index


def neighbours(index):
    row, column = divmod(index, 10)
    cells = []
    if row > 0:
        cells.append(index - 10)
    if row < 9:
        cells.append(index + 10)
    if column > 0:
        cells.append(index - 1)
    if column < 9:
        cells.append(index + 1)
    return cells


def ships_from_hits(hits):
    ships = []
    for cell in sorted(hits):
        touched = [ship for ship in ships if any(near in ship for near in neighbours(cell))]
        ships = [ship for ship in ships if ship not in touched]
        ships.append(set.union({cell}, *touched))
    return ships


def finishing_cells(ship):
    if len(ship) == 1:
        return set(neighbours(next(iter(ship))))

    step = 1 if len({cell // 10 for cell in ship}) == 1 else 10
    ends = {min(ship) - step, max(ship) + step}
    reachable = set(neighbours(min(ship)) + neighbours(max(ship)))
    return ends & reachable


def choose_shot(history):
    fired = {to_index(cell) for cell, _ in history}
    hits = {to_index(cell) for cell, result in history if result in ("hit", "killed")}
    killed = {to_index(cell) for cell, result in history if result == "killed"}

    ships = ships_from_hits(hits)
    wounded = [ship for ship in ships if not ship & killed]
    sunk = [ship for ship in ships if ship & killed]

    targets = set()
    for ship in wounded:
        targets |= finishing_cells(ship)
    targets -= fired
    if targets:
        return to_coordinate(random.choice(sorted(targets)))

    empty = set()
    for ship in sunk:
        for cell in ship:
            empty |= around(cell)

    free = [cell for cell in range(100) if cell not in fired and cell not in empty]
    if not free:
        free = [cell for cell in range(100) if cell not in fired]
    if not free:
        raise RuntimeError("the whole board is already fired at")

    spread = [cell for cell in free if sum(divmod(cell, 10)) % 2 == 0]
    return to_coordinate(random.choice(spread or free))
