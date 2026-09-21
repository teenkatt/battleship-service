import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Uuid,
    create_engine,
    delete,
    insert,
    select,
)

from battleship.settings import settings

engine = create_engine(settings.database_url)
metadata = MetaData()

games = Table(
    "games",
    metadata,
    Column("id", Uuid, primary_key=True),
    Column("status", String(10), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

ship_cells = Table(
    "ship_cells",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("game_id", Uuid, ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
    Column("ship_number", Integer, nullable=False),
    Column("cell", String(3), nullable=False),
    Column("is_hit", Boolean, nullable=False),
)


def save_new_game(ships):
    game_id = uuid.uuid4()
    rows = []
    for number, ship in enumerate(ships):
        for cell in ship:
            rows.append({"game_id": game_id, "ship_number": number, "cell": cell, "is_hit": False})

    with engine.begin() as conn:
        conn.execute(insert(games).values(id=game_id, status="open", created_at=datetime.now(timezone.utc)))
        conn.execute(insert(ship_cells), rows)

    return game_id


def load_ships(game_id):
    query = (
        select(ship_cells.c.ship_number, ship_cells.c.cell)
        .where(ship_cells.c.game_id == game_id)
        .order_by(ship_cells.c.id)
    )
    ships = {}
    with engine.connect() as conn:
        for number, cell in conn.execute(query):
            ships.setdefault(number, []).append(cell)
    return [ships[number] for number in sorted(ships)]


def remove_game(game_id):
    with engine.begin() as conn:
        conn.execute(delete(ship_cells).where(ship_cells.c.game_id == game_id))
        conn.execute(delete(games).where(games.c.id == game_id))
