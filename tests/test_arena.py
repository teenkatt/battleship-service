import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from arena.client import Service
from arena.match import play
from battleship.main import app
from battleship.placement import generate_fleet


def connect(name, target):
    return Service(name, client=TestClient(target))


def fake_app(fleet, result="miss", closed=None):
    fake = FastAPI()

    @fake.post("/game", status_code=201)
    def start_game():
        return {"session_id": "11111111-1111-1111-1111-111111111111", "ships": [{"coordinates": ship} for ship in fleet]}

    @fake.post("/game/{session_id}/shot")
    def make_shot(session_id: str):
        return {"coordinate": "A1"}

    @fake.post("/game/{session_id}/shot/result")
    def accept_result(session_id: str):
        return {"status": "accepted"}

    @fake.post("/game/{session_id}/opponent-shot")
    def opponent_shot(session_id: str):
        return {"result": result}

    @fake.post("/game/{session_id}/close")
    def close_session(session_id: str):
        if closed is not None:
            closed.append(session_id)
        return {"status": "closed"}

    return fake


class Repeater:
    def __init__(self, name, fleet):
        self.name = name
        self.fleet = fleet
        self.taken = set()
        self.results = []

    def start_game(self):
        return "22222222-2222-2222-2222-222222222222", self.fleet

    def ask_shot(self, session_id):
        return "A1"

    def ask_opponent_shot(self, session_id, coordinate):
        self.taken.add(coordinate)
        for ship in self.fleet:
            if coordinate in ship:
                return "killed" if set(ship) <= self.taken else "hit"
        return "miss"

    def send_result(self, session_id, result):
        self.results.append(result)

    def close(self, session_id):
        pass


@pytest.fixture
def quiet():
    return lambda message: None


def test_match_between_two_services_ends_with_a_winner(quiet):
    result = play(connect("left", app), connect("right", app), quiet)

    assert result["winner"] in ("left", "right")
    assert result["reason"] == "флот потоплен"


def test_invalid_placement_loses_the_match(quiet):
    broken = fake_app(generate_fleet()[:-1])

    result = play(connect("broken", broken), connect("honest", app), quiet)

    assert result["winner"] == "honest"
    assert "расстановка" in result["reason"]


def test_lying_service_loses_the_match_and_sessions_are_closed(quiet):
    closed = []
    liar = fake_app(generate_fleet(), closed=closed)

    result = play(connect("honest", app), connect("liar", liar), quiet)

    assert result["winner"] == "honest"
    assert "вместо" in result["reason"]
    assert closed == ["11111111-1111-1111-1111-111111111111"]


def test_slow_service_loses_the_match(quiet):
    def too_slow(request):
        raise httpx.TimeoutException("too slow", request=request)

    slow = Service("slow", client=httpx.Client(transport=httpx.MockTransport(too_slow), base_url="http://slow"))

    result = play(slow, connect("fast", app), quiet)

    assert result["winner"] == "fast"
    assert "дольше" in result["reason"]


def test_repeated_shot_passes_the_turn_but_gets_its_result(quiet):
    repeater = Repeater("repeater", generate_fleet())

    result = play(repeater, connect("honest", app), quiet)

    assert result["winner"] == "honest"
    assert len(repeater.results) > 1
