import uuid

import pytest

from battleship.placement import LETTERS


def fleet_of(game):
    return [ship["coordinates"] for ship in game["ships"]]


def shoot(api, game, coordinate):
    return api.post(f"/game/{game['session_id']}/opponent-shot", json={"coordinate": coordinate})


def honest_answer(fleet, already_hit, coordinate):
    for ship in fleet:
        if coordinate in ship:
            return "killed" if set(ship) <= already_hit | {coordinate} else "hit"
    return "miss"


def test_single_deck_ship_dies_from_one_shot(api, game):
    ship = next(ship for ship in fleet_of(game) if len(ship) == 1)

    response = shoot(api, game, ship[0])

    assert response.status_code == 200
    assert response.json() == {"result": "killed"}


def test_four_deck_ship_dies_only_from_the_last_shot(api, game):
    ship = next(ship for ship in fleet_of(game) if len(ship) == 4)

    answers = [shoot(api, game, cell).json()["result"] for cell in ship]

    assert answers == ["hit", "hit", "hit", "killed"]


def test_shot_at_an_empty_cell_is_a_miss(api, game):
    busy = {cell for ship in fleet_of(game) for cell in ship}
    empty = next(
        cell
        for number in range(1, 11)
        for cell in (f"{letter}{number}" for letter in LETTERS)
        if cell not in busy
    )

    assert shoot(api, game, empty).json() == {"result": "miss"}


def test_every_answer_matches_the_placement(api, game):
    fleet = fleet_of(game)
    already_hit = set()

    for number in range(1, 11):
        for letter in LETTERS:
            coordinate = f"{letter}{number}"
            expected = honest_answer(fleet, already_hit, coordinate)

            assert shoot(api, game, coordinate).json() == {"result": expected}, coordinate
            already_hit.add(coordinate)


def test_repeated_shot_keeps_the_same_answer(api, game):
    ship = next(ship for ship in fleet_of(game) if len(ship) == 1)

    first = shoot(api, game, ship[0]).json()
    second = shoot(api, game, ship[0]).json()

    assert first == second == {"result": "killed"}


def test_games_do_not_share_their_fields(api, game, created_games):
    other = api.post("/game").json()
    created_games.append(uuid.UUID(other["session_id"]))
    cell = next(ship for ship in fleet_of(game) if len(ship) == 1)[0]

    shoot(api, game, cell)

    expected = honest_answer(fleet_of(other), set(), cell)
    assert shoot(api, other, cell).json() == {"result": expected}


@pytest.mark.parametrize("coordinate", ["", "A0", "A11", "K5", "a5", "A05", "1A"])
def test_bad_coordinate_is_rejected(api, game, coordinate):
    response = shoot(api, game, coordinate)

    assert response.status_code == 400
    assert set(response.json()) == {"detail"}


def test_request_without_coordinate_is_rejected(api, game):
    response = api.post(f"/game/{game['session_id']}/opponent-shot", json={})

    assert response.status_code == 400


@pytest.mark.parametrize("session_id", [str(uuid.uuid4()), "not-a-uuid"])
def test_unknown_session_is_not_found(api, session_id):
    response = api.post(f"/game/{session_id}/opponent-shot", json={"coordinate": "A1"})

    assert response.status_code == 404
