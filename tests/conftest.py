import uuid

import pytest
from fastapi.testclient import TestClient

from battleship.main import app
from battleship.storage import engine, metadata, remove_game

if engine.dialect.name == "sqlite":
    metadata.create_all(engine)


@pytest.fixture
def api():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def created_games():
    game_ids = []
    yield game_ids
    for game_id in game_ids:
        remove_game(game_id)


@pytest.fixture
def game(api, created_games):
    body = api.post("/game").json()
    created_games.append(uuid.UUID(body["session_id"]))
    return body
