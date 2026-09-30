from battleship.placement import to_index
from battleship.targeting import choose_shot, ships_from_hits

AROUND_E5 = {"D4", "D5", "D6", "E4", "E5", "E6", "F4", "F5", "F6"}


def test_first_shot_is_on_the_board():
    assert 0 <= to_index(choose_shot([])) < 100


def test_fired_cells_are_never_chosen_again():
    history = [(f"{letter}{number}", "miss") for letter in "ABCDEFGHI" for number in range(1, 11)]

    for _ in range(20):
        assert choose_shot(history).startswith("J")


def test_single_hit_is_attacked_from_four_sides():
    for _ in range(20):
        assert choose_shot([("E5", "hit")]) in {"D5", "F5", "E4", "E6"}


def test_wounded_ship_is_finished_from_its_ends():
    for _ in range(20):
        assert choose_shot([("E5", "hit"), ("E6", "hit")]) in {"E4", "E7"}


def test_cells_around_a_sunk_ship_are_not_attacked():
    for _ in range(50):
        assert choose_shot([("E5", "killed")]) not in AROUND_E5


def test_touching_hits_are_one_ship_and_distant_ones_are_not():
    assert len(ships_from_hits({to_index("E5"), to_index("E6")})) == 1
    assert len(ships_from_hits({to_index("A1"), to_index("J10")})) == 2
