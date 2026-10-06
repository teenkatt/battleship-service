import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from battleship.storage import load_ships

GAMES = 10


def play(api):
    body = api.post("/game").json()
    session_id = body["session_id"]
    single_deck = next(ship["coordinates"][0] for ship in body["ships"] if len(ship["coordinates"]) == 1)

    answer = api.post(f"/game/{session_id}/opponent-shot", json={"coordinate": single_deck}).json()
    shot = api.post(f"/game/{session_id}/shot").json()
    api.post(f"/game/{session_id}/shot/result", json={"result": "miss"})
    closed = api.post(f"/game/{session_id}/close").json()

    return {"body": body, "answer": answer, "shot": shot, "closed": closed}


def test_parallel_games_keep_their_own_state(api, created_games):
    with ThreadPoolExecutor(max_workers=GAMES) as pool:
        games = list(pool.map(lambda _: play(api), range(GAMES)))

    for game in games:
        created_games.append(uuid.UUID(game["body"]["session_id"]))

    assert len({game["body"]["session_id"] for game in games}) == GAMES
    for game in games:
        assert game["answer"] == {"result": "killed"}
        assert game["closed"] == {"status": "closed"}

        stored = load_ships(uuid.UUID(game["body"]["session_id"]))
        answered = [ship["coordinates"] for ship in game["body"]["ships"]]
        assert stored == answered


def test_every_answer_fits_in_a_second(api, created_games):
    def timed(_):
        started = time.perf_counter()
        body = api.post("/game").json()
        created = time.perf_counter()
        api.post(f"/game/{body['session_id']}/shot")
        return body["session_id"], created - started, time.perf_counter() - created

    with ThreadPoolExecutor(max_workers=GAMES) as pool:
        measured = list(pool.map(timed, range(GAMES)))

    for session_id, start_time, shot_time in measured:
        created_games.append(uuid.UUID(session_id))
        assert start_time < 1
        assert shot_time < 1


def test_two_shots_at_once_take_only_one_turn(api, game):
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = [r.status_code for r in pool.map(lambda _: api.post(f"/game/{game['session_id']}/shot"), range(2))]

    assert sorted(codes) == [200, 409]


def test_two_closes_at_once_leave_one_success(api, game):
    with ThreadPoolExecutor(max_workers=2) as pool:
        codes = [r.status_code for r in pool.map(lambda _: api.post(f"/game/{game['session_id']}/close"), range(2))]

    assert sorted(codes) == [200, 400]


def test_ship_is_killed_once_even_under_parallel_shots(api, game):
    ship = next(ship["coordinates"] for ship in game["ships"] if len(ship["coordinates"]) == 4)

    def shoot(cell):
        return api.post(f"/game/{game['session_id']}/opponent-shot", json={"coordinate": cell}).json()

    with ThreadPoolExecutor(max_workers=4) as pool:
        answers = [answer["result"] for answer in pool.map(shoot, ship)]

    assert sorted(answers) == ["hit", "hit", "hit", "killed"]
