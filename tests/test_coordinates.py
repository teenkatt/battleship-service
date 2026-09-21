import pytest

from battleship.placement import PlacementError, to_coordinate, to_index


@pytest.mark.parametrize("coordinate, index", [("A1", 0), ("J1", 9), ("A10", 90), ("J10", 99)])
def test_coordinate_to_index_and_back(coordinate, index):
    assert to_index(coordinate) == index
    assert to_coordinate(index) == coordinate


@pytest.mark.parametrize("coordinate", ["", "A0", "A11", "K5", "a5", "A05"])
def test_bad_coordinate_is_rejected(coordinate):
    with pytest.raises(PlacementError, match="bad coordinate"):
        to_index(coordinate)
