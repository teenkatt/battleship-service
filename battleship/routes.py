import uuid
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from battleship.placement import PlacementError, generate_fleet, to_index
from battleship.storage import (
    close_game,
    game_status,
    hit_own_fleet,
    load_ships,
    save_new_game,
    save_next_shot,
    save_shot_result,
)
from battleship.targeting import choose_shot

router = APIRouter()

SESSION_ERRORS = {404: {"description": "Session not found"}, 410: {"description": "Session is finished"}}


class ShipOut(BaseModel):
    coordinates: list[str]


class GameCreated(BaseModel):
    session_id: uuid.UUID
    ships: list[ShipOut]


class CoordinateIn(BaseModel):
    coordinate: str


class CoordinateOut(BaseModel):
    coordinate: str


class ShotResultIn(BaseModel):
    result: Literal["miss", "hit", "killed"]


class ShotResultOut(BaseModel):
    result: Literal["miss", "hit", "killed"]


class Accepted(BaseModel):
    status: Literal["accepted"]


class Closed(BaseModel):
    status: Literal["closed"]


def open_game(session_id):
    try:
        game_id = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    status = game_status(game_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if status != "open":
        raise HTTPException(status_code=410, detail="Session is finished")
    return game_id


@router.post(
    "/game",
    status_code=201,
    response_model=GameCreated,
    responses={500: {"description": "Unexpected error"}},
)
def start_game():
    game_id = save_new_game(generate_fleet())
    ships = load_ships(game_id)
    return GameCreated(session_id=game_id, ships=[ShipOut(coordinates=ship) for ship in ships])


@router.post(
    "/game/{session_id}/opponent-shot",
    response_model=ShotResultOut,
    responses=SESSION_ERRORS | {400: {"description": "Bad coordinate"}},
)
def opponent_shot(session_id: str, body: CoordinateIn):
    game_id = open_game(session_id)
    try:
        to_index(body.coordinate)
    except PlacementError:
        raise HTTPException(status_code=400, detail="Bad coordinate")

    return ShotResultOut(result=hit_own_fleet(game_id, body.coordinate))


@router.post(
    "/game/{session_id}/shot",
    response_model=CoordinateOut,
    responses=SESSION_ERRORS | {409: {"description": "Previous shot has no result yet"}},
)
def make_shot(session_id: str):
    game_id = open_game(session_id)
    coordinate = save_next_shot(game_id, choose_shot)
    if coordinate is None:
        raise HTTPException(status_code=409, detail="Previous shot has no result yet")

    return CoordinateOut(coordinate=coordinate)


@router.post(
    "/game/{session_id}/shot/result",
    response_model=Accepted,
    responses=SESSION_ERRORS | {400: {"description": "Bad result"}, 409: {"description": "No shot is waiting for a result"}},
)
def accept_shot_result(session_id: str, body: ShotResultIn):
    game_id = open_game(session_id)
    if not save_shot_result(game_id, body.result):
        raise HTTPException(status_code=409, detail="No shot is waiting for a result")

    return Accepted(status="accepted")


@router.post(
    "/game/{session_id}/close",
    response_model=Closed,
    responses={400: {"description": "Session is closed already"}, 404: {"description": "Session not found"}},
)
def close_session(session_id: str):
    try:
        game_id = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    closing = close_game(game_id)
    if closing == "unknown":
        raise HTTPException(status_code=404, detail="Session not found")
    if closing == "closed already":
        raise HTTPException(status_code=400, detail="Session is closed already")

    return Closed(status="closed")
