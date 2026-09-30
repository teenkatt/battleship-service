import uuid

import pytest


def close(api, session_id):
    return api.post(f"/game/{session_id}/close")


def test_session_is_closed_once(api, game):
    response = close(api, game["session_id"])

    assert response.status_code == 200
    assert response.json() == {"status": "closed"}


def test_second_close_is_a_bad_request(api, game):
    close(api, game["session_id"])

    response = close(api, game["session_id"])

    assert response.status_code == 400
    assert set(response.json()) == {"detail"}


@pytest.mark.parametrize("session_id", [str(uuid.uuid4()), "not-a-uuid"])
def test_unknown_session_is_not_found(api, session_id):
    assert close(api, session_id).status_code == 404


def test_closed_session_does_not_play_anymore(api, game):
    session_id = game["session_id"]
    close(api, session_id)

    assert api.post(f"/game/{session_id}/shot").status_code == 410
    assert api.post(f"/game/{session_id}/shot/result", json={"result": "miss"}).status_code == 410
    assert api.post(f"/game/{session_id}/opponent-shot", json={"coordinate": "A1"}).status_code == 410


def test_closing_one_session_does_not_touch_another(api, game, created_games):
    other = api.post("/game").json()
    created_games.append(uuid.UUID(other["session_id"]))

    close(api, game["session_id"])

    assert api.post(f"/game/{other['session_id']}/shot").status_code == 200
