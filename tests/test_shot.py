import re
import uuid

import pytest

from battleship.placement import generate_fleet, to_index
from battleship.targeting import neighbours

COORDINATE = re.compile(r"[A-J](10|[1-9])")


def shoot(api, game):
    return api.post(f"/game/{game['session_id']}/shot")


def answer(api, game, result):
    return api.post(f"/game/{game['session_id']}/shot/result", json={"result": result})


def test_shot_returns_a_coordinate_on_the_board(api, game):
    response = shoot(api, game)

    assert response.status_code == 200
    assert COORDINATE.fullmatch(response.json()["coordinate"])


def test_next_shot_waits_for_the_result_of_the_previous_one(api, game):
    shoot(api, game)

    assert shoot(api, game).status_code == 409

    assert answer(api, game, "miss").json() == {"status": "accepted"}
    assert shoot(api, game).status_code == 200


def test_result_without_a_shot_is_a_conflict(api, game):
    assert answer(api, game, "miss").status_code == 409


@pytest.mark.parametrize("body", [{"result": "boom"}, {"result": ""}, {}, {"outcome": "hit"}])
def test_bad_result_is_rejected(api, game, body):
    shoot(api, game)

    response = api.post(f"/game/{game['session_id']}/shot/result", json=body)

    assert response.status_code == 400
    assert set(response.json()) == {"detail"}


def test_service_never_repeats_a_shot(api, game):
    fired = []
    for _ in range(100):
        fired.append(shoot(api, game).json()["coordinate"])
        answer(api, game, "miss")

    assert len(set(fired)) == 100


def test_service_finishes_a_wounded_ship(api, game):
    wounded = shoot(api, game).json()["coordinate"]
    answer(api, game, "hit")

    next_shot = shoot(api, game).json()["coordinate"]

    assert to_index(next_shot) in neighbours(to_index(wounded))


def test_service_sinks_a_whole_fleet(api, game):
    fleet = [set(ship) for ship in generate_fleet()]
    fired = set()

    while not all(ship <= fired for ship in fleet):
        coordinate = shoot(api, game).json()["coordinate"]
        assert coordinate not in fired
        fired.add(coordinate)

        ship = next((ship for ship in fleet if coordinate in ship), None)
        if ship is None:
            answer(api, game, "miss")
        else:
            answer(api, game, "killed" if ship <= fired else "hit")

    assert len(fired) < 90


@pytest.mark.parametrize("path", ["/shot", "/shot/result"])
def test_unknown_session_is_not_found(api, path):
    response = api.post(f"/game/{uuid.uuid4()}{path}", json={"result": "miss"})

    assert response.status_code == 404
