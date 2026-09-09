import random

LETTERS = "ABCDEFGHIJ"
SIZE = 10
FLEET = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]


def to_coordinate(x, y):
    return LETTERS[x] + str(y + 1)


def from_coordinate(coordinate):
    if len(coordinate) < 2:
        return None

    letter = coordinate[0]
    number = coordinate[1:]

    if letter not in LETTERS or not number.isdigit():
        return None

    y = int(number)
    if y < 1 or y > SIZE:
        return None

    return LETTERS.index(letter), y - 1


def get_cells(ship):
    cells = []
    for coordinate in ship["coordinates"]:
        cell = from_coordinate(coordinate)
        if cell is None:
            return None
        cells.append(cell)
    return cells


def neighbours(x, y):
    cells = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = x + dx
            ny = y + dy
            if 0 <= nx < SIZE and 0 <= ny < SIZE:
                cells.append((nx, ny))
    return cells


def is_line(cells):
    if len(cells) == 1:
        return True

    columns = [x for x, y in cells]
    rows = [y for x, y in cells]

    if len(set(columns)) == 1:
        line = sorted(rows)
    elif len(set(rows)) == 1:
        line = sorted(columns)
    else:
        return False

    for i in range(1, len(line)):
        if line[i] != line[i - 1] + 1:
            return False

    return True


def empty_field():
    return [[0] * SIZE for _ in range(SIZE)]


def place_is_free(field, cells):
    for x, y in cells:
        for nx, ny in neighbours(x, y):
            if field[ny][nx] != 0:
                return False
    return True


def check_fleet(ships):
    field = empty_field()
    sizes = []

    for number, ship in enumerate(ships, start=1):
        cells = get_cells(ship)

        if not cells:
            return False
        if len(set(cells)) != len(cells):
            return False
        if not is_line(cells):
            return False
        if not place_is_free(field, cells):
            return False

        for x, y in cells:
            field[y][x] = number

        sizes.append(len(cells))

    return sorted(sizes, reverse=True) == FLEET


def random_cells(size):
    horizontal = random.choice([True, False])

    if horizontal:
        x = random.randint(0, SIZE - size)
        y = random.randint(0, SIZE - 1)
        return [(x + i, y) for i in range(size)]

    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - size)
    return [(x, y + i) for i in range(size)]


def find_place(field, size):
    for attempt in range(500):
        cells = random_cells(size)
        if place_is_free(field, cells):
            return cells
    return None


def generate_fleet():
    for attempt in range(100):
        field = empty_field()
        ships = []

        for size in FLEET:
            cells = find_place(field, size)
            if cells is None:
                break

            for x, y in cells:
                field[y][x] = 1

            ships.append({"coordinates": [to_coordinate(x, y) for x, y in cells]})

        if len(ships) == len(FLEET):
            return ships

    raise RuntimeError("не удалось расставить флот")
