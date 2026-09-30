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
    func,
    insert,
    select,
    update,
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

shots = Table(
    "shots",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("game_id", Uuid, ForeignKey("games.id", ondelete="CASCADE"), nullable=False),
    Column("cell", String(3), nullable=False),
    Column("result", String(6)),
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


def game_status(game_id):
    with engine.connect() as conn:
        return conn.execute(select(games.c.status).where(games.c.id == game_id)).scalar()


def hit_own_fleet(game_id, cell):
    with engine.begin() as conn:
        ship_number = conn.execute(
            select(ship_cells.c.ship_number).where(
                ship_cells.c.game_id == game_id, ship_cells.c.cell == cell
            )
        ).scalar()
        if ship_number is None:
            return "miss"

        conn.execute(
            update(ship_cells)
            .where(ship_cells.c.game_id == game_id, ship_cells.c.cell == cell)
            .values(is_hit=True)
        )
        alive = conn.execute(
            select(func.count())
            .select_from(ship_cells)
            .where(
                ship_cells.c.game_id == game_id,
                ship_cells.c.ship_number == ship_number,
                ship_cells.c.is_hit.is_(False),
            )
        ).scalar()

    return "killed" if alive == 0 else "hit"


def load_shots(game_id):
    query = select(shots.c.cell, shots.c.result).where(shots.c.game_id == game_id).order_by(shots.c.id)
    with engine.connect() as conn:
        return list(conn.execute(query))


def save_shot(game_id, cell):
    with engine.begin() as conn:
        conn.execute(insert(shots).values(game_id=game_id, cell=cell))


def save_shot_result(game_id, result):
    with engine.begin() as conn:
        pending = conn.execute(
            select(shots.c.id).where(shots.c.game_id == game_id, shots.c.result.is_(None))
        ).scalar()
        if pending is None:
            return False
        conn.execute(update(shots).where(shots.c.id == pending).values(result=result))
    return True


def remove_game(game_id):
    with engine.begin() as conn:
        conn.execute(delete(shots).where(shots.c.game_id == game_id))
        conn.execute(delete(ship_cells).where(ship_cells.c.game_id == game_id))
        conn.execute(delete(games).where(games.c.id == game_id))
