import random
import re
from collections import Counter

LETTERS = "ABCDEFGHIJ"
REQUIRED_FLEET = Counter({4: 1, 3: 2, 2: 3, 1: 4})
COORDINATE_RE = re.compile(r"([A-J])(10|[1-9])")


class PlacementError(ValueError):
    pass


def to_index(coordinate):
    match = COORDINATE_RE.fullmatch(coordinate) if isinstance(coordinate, str) else None
    if match is None:
        raise PlacementError(f"bad coordinate {coordinate!r}")
    column = LETTERS.index(match.group(1))
    row = int(match.group(2)) - 1
    return row * 10 + column


def to_coordinate(index):
    row, column = divmod(index, 10)
    return f"{LETTERS[column]}{row + 1}"


def around(index):
    row, column = divmod(index, 10)
    cells = set()
    for r in range(row - 1, row + 2):
        for c in range(column - 1, column + 2):
            if 0 <= r < 10 and 0 <= c < 10:
                cells.add(r * 10 + c)
    return cells


def check_placement(ships):
    taken = {}
    lengths = Counter()

    for number, ship in enumerate(ships):
        if not ship:
            raise PlacementError(f"ship {number} has no cells")

        cells = [to_index(coordinate) for coordinate in ship]
        if len(set(cells)) != len(cells):
            raise PlacementError(f"ship {number} has repeated cells")

        rows = {cell // 10 for cell in cells}
        columns = {cell % 10 for cell in cells}
        if len(rows) > 1 and len(columns) > 1:
            raise PlacementError(f"ship {number} is not straight")

        step = 1 if len(rows) == 1 else 10
        if max(cells) - min(cells) != (len(cells) - 1) * step:
            raise PlacementError(f"ship {number} has a gap")

        for cell in cells:
            if cell in taken:
                raise PlacementError(f"ships {taken[cell]} and {number} overlap")

        for cell in cells:
            for near in around(cell):
                if near in taken:
                    raise PlacementError(f"ships {taken[near]} and {number} touch")

        for cell in cells:
            taken[cell] = number
        lengths[len(cells)] += 1

    if lengths != REQUIRED_FLEET:
        raise PlacementError(f"wrong fleet: {dict(sorted(lengths.items()))}")


def is_valid_placement(ships):
    try:
        check_placement(ships)
    except PlacementError:
        return False
    return True


def free_positions(length, blocked):
    positions = []
    for row in range(10):
        for column in range(10):
            if column + length <= 10:
                horizontal = [row * 10 + column + step for step in range(length)]
                if not blocked.intersection(horizontal):
                    positions.append(horizontal)
            if length > 1 and row + length <= 10:
                vertical = [(row + step) * 10 + column for step in range(length)]
                if not blocked.intersection(vertical):
                    positions.append(vertical)
    return positions


def generate_fleet():
    lengths = sorted(REQUIRED_FLEET.elements(), reverse=True)

    for _ in range(50):
        blocked = set()
        ships = []
        for length in lengths:
            positions = free_positions(length, blocked)
            if not positions:
                break
            cells = random.choice(positions)
            ships.append([to_coordinate(cell) for cell in cells])
            for cell in cells:
                blocked |= around(cell)

        if len(ships) == len(lengths):
            return ships

    raise RuntimeError("could not place the fleet")
