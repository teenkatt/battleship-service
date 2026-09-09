import uuid

from pydantic import BaseModel


class ShipSchema(BaseModel):
    coordinates: list[str]


class NewGameResponse(BaseModel):
    session_id: uuid.UUID
    ships: list[ShipSchema]
