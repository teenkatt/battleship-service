from collections import Counter

from battleship.placement import REQUIRED_FLEET, check_placement, generate_fleet, to_index


def test_generated_fleet_passes_rules_check():
    for _ in range(300):
        check_placement(generate_fleet())


def test_generated_fleet_has_right_lengths():
    fleet = generate_fleet()
    assert len(fleet) == 10
    assert Counter(len(ship) for ship in fleet) == REQUIRED_FLEET


def test_generated_ships_have_empty_border():
    for _ in range(100):
        fleet = generate_fleet()
        board = [[None] * 12 for _ in range(12)]
        for number, ship in enumerate(fleet):
            for coordinate in ship:
                row, column = divmod(to_index(coordinate), 10)
                board[row + 1][column + 1] = number

        for number, ship in enumerate(fleet):
            for coordinate in ship:
                row, column = divmod(to_index(coordinate), 10)
                for r in range(row, row + 3):
                    for c in range(column, column + 3):
                        assert board[r][c] in (None, number)
