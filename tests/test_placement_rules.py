import pytest

from battleship.placement import PlacementError, check_placement, is_valid_placement

SAMPLE = [
    ["B2", "C2", "D2", "E2"],
    ["H1", "H2", "H3"],
    ["A5", "A6", "A7"],
    ["D5", "E5"],
    ["J6", "J7"],
    ["C9", "D9"],
    ["G8"],
    ["J10"],
    ["F10"],
    ["H5"],
]


def with_ship(position, cells):
    fleet = [list(ship) for ship in SAMPLE]
    fleet[position] = cells
    return fleet


def test_sample_fleet_is_accepted():
    check_placement(SAMPLE)
    assert is_valid_placement(SAMPLE)


@pytest.mark.parametrize(
    "fleet, reason",
    [
        pytest.param(SAMPLE[:-1], "wrong fleet", id="one ship missing"),
        pytest.param(SAMPLE + [["A10"]], "wrong fleet", id="extra ship"),
        pytest.param(with_ship(2, ["A5", "A6", "A7", "A8"]), "wrong fleet", id="two four-deckers"),
        pytest.param(with_ship(3, ["D5", "E6"]), "not straight", id="diagonal ship"),
        pytest.param(with_ship(1, ["H1", "H2", "H4"]), "gap", id="ship with gap"),
        pytest.param(with_ship(5, ["C9", "C9"]), "repeated", id="same cell twice"),
        pytest.param(with_ship(4, ["J10", "J11"]), "bad coordinate", id="ship leaves board"),
        pytest.param(with_ship(7, ["E2"]), "overlap", id="ships overlap"),
        pytest.param(with_ship(6, ["G10"]), "touch", id="touch by side"),
        pytest.param(with_ship(7, ["I8"]), "touch", id="touch by corner"),
    ],
)
def test_broken_fleet_is_rejected(fleet, reason):
    with pytest.raises(PlacementError, match=reason):
        check_placement(fleet)
    assert not is_valid_placement(fleet)
