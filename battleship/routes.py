import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from battleship.placement import generate_fleet
from battleship.storage import load_ships, save_new_game

router = APIRouter()


class ShipOut(BaseModel):
    coordinates: list[str]


class GameCreated(BaseModel):
    session_id: uuid.UUID
    ships: list[ShipOut]


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
