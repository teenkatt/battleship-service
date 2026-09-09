from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import get_db
from models import Game
from schemas import NewGameResponse
from ships import generate_fleet

app = FastAPI(title="Battleship service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/game", response_model=NewGameResponse, status_code=201)
def new_game(db: Session = Depends(get_db)):
    ships = generate_fleet()

    game = Game(ships=ships)
    db.add(game)
    db.commit()
    db.refresh(game)

    return {"session_id": game.session_id, "ships": ships}
