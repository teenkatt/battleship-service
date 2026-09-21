import uuid

from sqlalchemy import func, select

from battleship.placement import check_placement
from battleship.storage import engine, games, ship_cells


def start(api, created_games, **kwargs):
    response = api.post("/game", **kwargs)
    if response.status_code == 201:
        created_games.append(uuid.UUID(response.json()["session_id"]))
    return response


def count_games():
    with engine.connect() as conn:
        return conn.execute(select(func.count()).select_from(games)).scalar()


def test_start_game_answer_matches_contract(api, created_games):
    response = start(api, created_games)
    body = response.json()

    assert response.status_code == 201
    assert set(body) == {"session_id", "ships"}
    assert all(set(ship) == {"coordinates"} for ship in body["ships"])
    uuid.UUID(body["session_id"])


def test_returned_fleet_follows_rules(api, created_games):
    body = start(api, created_games).json()

    check_placement([ship["coordinates"] for ship in body["ships"]])


def test_game_and_cells_are_stored(api, created_games):
    body = start(api, created_games).json()
    game_id = uuid.UUID(body["session_id"])

    with engine.connect() as conn:
        game = conn.execute(select(games).where(games.c.id == game_id)).one()
        rows = conn.execute(
            select(ship_cells.c.ship_number, ship_cells.c.cell).where(ship_cells.c.game_id == game_id)
        ).all()

    assert game.status == "open"
    stored = {}
    for number, cell in rows:
        stored.setdefault(number, set()).add(cell)
    answered = {number: set(ship["coordinates"]) for number, ship in enumerate(body["ships"])}
    assert stored == answered


def test_two_games_are_stored_separately(api, created_games):
    first = start(api, created_games).json()
    second = start(api, created_games).json()

    assert first["session_id"] != second["session_id"]
    with engine.connect() as conn:
        for body in (first, second):
            cells = conn.execute(
                select(func.count())
                .select_from(ship_cells)
                .where(ship_cells.c.game_id == uuid.UUID(body["session_id"]))
            ).scalar()
            assert cells == 20


def test_request_body_does_not_change_anything(api, created_games):
    foreign_id = str(uuid.uuid4())

    response = start(api, created_games, json={"session_id": foreign_id, "ships": [["A1"]]})

    assert response.status_code == 201
    assert response.json()["session_id"] != foreign_id


def test_crash_inside_handler_gives_json_500(api, monkeypatch):
    def broken_generator():
        raise RuntimeError("generator is broken")

    monkeypatch.setattr("battleship.routes.generate_fleet", broken_generator)
    games_before = count_games()

    response = api.post("/game")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert count_games() == games_before
